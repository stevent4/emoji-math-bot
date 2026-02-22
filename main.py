import asyncio
import random
import time
import warnings
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.client.session.aiohttp import AiohttpSession

# Import fungsi dari file modular (Pastikan file database.py yang baru dan image_engine.py sudah ada)
from database import init_db, get_or_create_player, update_player_score, get_leaderboard, buy_item, use_freeze_item
from image_engine import generate_math_image

warnings.filterwarnings("ignore", category=UserWarning)

# === CONFIGURATION ===
TOKEN = "[Masukan Token Botmu]"

# SETTING NORMAL UNTUK VPS (Tanpa Proxy)
bot = Bot(token=TOKEN)
dp = Dispatcher()

EMOJI_ASSETS = {
    '🍎': 'assets/apple.png', '🍌': 'assets/banana.png',
    '🍇': 'assets/grape.png', '🍉': 'assets/watermelon.png',
    '🍓': 'assets/strawberry.png', '🍔': 'assets/burger.png',
    '🍕': 'assets/pizza.png', '🍩': 'assets/donut.png',
    '🥑': 'assets/avocado.png', '🌮': 'assets/taco.png',
    '🍦': 'assets/icecream.png', '💎': 'assets/diamond.png',
    '🔥': 'assets/fire.png'
}

# Katalog Barang di Shop
SHOP_ITEMS = {
    "item_freeze": {"name": "❄️ Freeze (+15 Detik)", "price": 20, "type": "consumable"},
    "buy_jenius": {"name": "🧠 Si Jenius", "price": 50, "type": "title"},
    "buy_raja": {"name": "👑 Raja Hitung", "price": 100, "type": "title"},
    "buy_speed": {"name": "⚡ Speedster", "price": 150, "type": "title"},
    "buy_dewa": {"name": "🌌 Dewa Matematika", "price": 500, "type": "title"}
}

active_games = {}

# === FUNGSI BACKGROUND: PERINGATAN 5 DETIK ===
async def warning_timer(chat_id, msg_id, original_caption, buttons):
    await asyncio.sleep(25) # Tunggu 25 detik

    # Jika game masih belum dijawab
    if msg_id in active_games:
        warning_caption = original_caption + "\n\n🚨 **CEPAT! WAKTU TINGGAL 5 DETIK!** 🚨"
        try:
            await bot.edit_message_caption(
                chat_id=chat_id,
                message_id=msg_id,
                caption=warning_caption,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
                parse_mode="Markdown"
            )
        except Exception:
            pass

# === HANDLER MENU UTAMA ===
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await get_or_create_player(message.from_user.id, message.from_user.first_name)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Mulai Main!", callback_data="menu_play")],
        [InlineKeyboardButton(text="📊 Leaderboard", callback_data="menu_rank"),
         InlineKeyboardButton(text="🛒 Buka Shop", callback_data="menu_shop")]
    ])
    welcome_text = (
        "👋 **Halo Jagoan! Selamat datang di arena Emoji Math PRO!** 🎯\n\n"
        "Uji seberapa cepat otakmu memproses angka dan gambar! "
        "Jawab dengan kilat ⚡ ➡️ Panen Koin 🪙 ➡️ Beli Gelar Sultan di Shop 🛒.\n\n"
        "Awas, salah pencet = Game Over! Siap pecahkan rekor hari ini?"
    )
    await message.answer(welcome_text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Mulai Main!", callback_data="menu_play")],
        [InlineKeyboardButton(text="📊 Leaderboard", callback_data="menu_rank"),
         InlineKeyboardButton(text="🛒 Buka Shop", callback_data="menu_shop")]
    ])
    try: await callback.message.delete()
    except: pass
    await callback.message.answer("👋 **Menu Utama Emoji Math PRO!** 🧠", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

# === HANDLER FITUR SHOP ===
@dp.callback_query(F.data == "menu_shop")
async def open_shop(callback: CallbackQuery):
    player = await get_or_create_player(callback.from_user.id, callback.from_user.first_name)

    text = (
        f"🛒 **EMOJI MATH SHOP** 🛒\n\n"
        f"🪙 Koin Kamu: **{player.coins}**\n"
        f"❄️ Item Freeze: **{player.freezes}x**\n\n"
        f"Pilih barang yang ingin dibeli:"
    )

    buttons = []
    for item_code, item_data in SHOP_ITEMS.items():
        buttons.append([InlineKeyboardButton(
            text=f"{item_data['name']} (🪙 {item_data['price']})",
            callback_data=item_code
        )])

    buttons.append([InlineKeyboardButton(text="🔙 Kembali", callback_data="menu_back")])

    try: await callback.message.delete()
    except: pass

    await callback.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.in_(SHOP_ITEMS.keys()))
async def process_buy(callback: CallbackQuery):
    item_code = callback.data
    item = SHOP_ITEMS[item_code]

    success = await buy_item(callback.from_user.id, item['type'], item['name'], item['price'])

    if success:
        if item['type'] == "title":
            await callback.answer(f"🎉 Pembelian Berhasil! Gelarmu sekarang: {item['name']}", show_alert=True)
        else:
            await callback.answer(f"🎉 Berhasil membeli 1x {item['name']}! Gunakan saat game berlangsung.", show_alert=True)
        await open_shop(callback)
    else:
        await callback.answer("❌ Koin kamu tidak cukup! Main lagi untuk mengumpulkan koin.", show_alert=True)

# === HANDLER GAME ENGINE ===
@dp.callback_query(F.data == "menu_play")
async def menu_play(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🟢 Easy", callback_data="diff_easy"),
         InlineKeyboardButton(text="🟡 Medium", callback_data="diff_medium")],
        [InlineKeyboardButton(text="🔴 Hard", callback_data="diff_hard")],
        [InlineKeyboardButton(text="🔙 Kembali", callback_data="menu_back")]
    ])

    try: await callback.message.delete()
    except: pass

    await callback.message.answer("🕹 **Pilih Level Kesulitan:**", reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("diff_"))
async def start_game(callback: CallbackQuery):
    diff = callback.data.split("_")[1]

    e1_char, e2_char = random.sample(list(EMOJI_ASSETS.keys()), 2)
    e1_path, e2_path = EMOJI_ASSETS[e1_char], EMOJI_ASSETS[e2_char]

    if diff == "easy":
        v1, v2 = random.randint(2, 10), random.randint(1, 9)
        xp_pts, coin_pts = 10, 2
        available_ops = ['+', '-']
    elif diff == "medium":
        v1, v2 = random.randint(10, 25), random.randint(2, 12)
        xp_pts, coin_pts = 30, 5
        available_ops = ['+', '-', '×']
    else: # hard
        v1, v2 = random.randint(15, 40), random.randint(5, 20)
        xp_pts, coin_pts = 50, 10
        available_ops = ['+', '-', '×']

    val1, val2 = max(v1, v2), min(v1, v2)
    info_op = random.choice(available_ops)
    tanya_op = random.choice([op for op in available_ops if op != info_op])

    if tanya_op == '+': correct_answer = val1 + val2
    elif tanya_op == '-': correct_answer = val1 - val2
    else: correct_answer = val1 * val2

    img_bytes = generate_math_image(e1_path, e2_path, val1, val2, info_op, tanya_op)
    photo = BufferedInputFile(img_bytes.read(), filename="math.png")

    options = {correct_answer}
    while len(options) < 4:
        fake_ans = correct_answer + random.randint(-15, 15)
        if fake_ans >= 0 and fake_ans != correct_answer:
            options.add(fake_ans)

    list_options = list(options)
    random.shuffle(list_options)

    # Susun Tombol Pilihan Jawaban
    buttons = [[InlineKeyboardButton(text=f"✨ {opt}", callback_data=f"ans_{opt}") for opt in list_options[:2]],
               [InlineKeyboardButton(text=f"✨ {opt}", callback_data=f"ans_{opt}") for opt in list_options[2:]]]

    # Tambahkan Tombol Item Freeze di bawah jawaban
    buttons.append([InlineKeyboardButton(text="❄️ Gunakan Freeze (+15s)", callback_data="use_freeze")])

    caption = f"🏆 **LEVEL: {diff.upper()}**\n⌛ *Waktu: 30 Detik*\n\nBerapa jawabannya?"

    try: await callback.message.delete()
    except: pass

    sent_msg = await callback.message.answer_photo(
        photo,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="Markdown"
    )

    active_games[sent_msg.message_id] = {
        "ans": correct_answer,
        "exp": time.time() + 30,
        "xp": xp_pts,
        "coins": coin_pts,
        "start_time": time.time(),
        "frozen": False # Penanda apakah sudah di-freeze
    }

    # Jalankan timer peringatan 5 detik di latar belakang
    asyncio.create_task(warning_timer(callback.message.chat.id, sent_msg.message_id, caption, buttons))

# === HANDLER PENGGUNAAN ITEM FREEZE ===
@dp.callback_query(F.data == "use_freeze")
async def apply_freeze(callback: CallbackQuery):
    msg_id = callback.message.message_id

    if msg_id not in active_games:
        return await callback.answer("Game sudah selesai!", show_alert=True)

    if active_games[msg_id].get("frozen"):
        return await callback.answer("Waktu sudah dibekukan di game ini!", show_alert=True)

    # Cek apakah user punya item freeze di inventory
    success = await use_freeze_item(callback.from_user.id)
    if success:
        # Tambah waktu 15 detik dan set frozen
        active_games[msg_id]["exp"] += 15
        active_games[msg_id]["frozen"] = True

        # Tambah info freeze ke caption
        new_caption = callback.message.caption + f"\n\n❄️ **WAKTU DITAMBAH +15 DETIK oleh {callback.from_user.first_name}!** ❄️"

        # Hilangkan tombol Freeze dari susunan keyboard (ambil elemen selain yang terakhir)
        buttons = callback.message.reply_markup.inline_keyboard[:-1]

        await callback.message.edit_caption(
            caption=new_caption,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            parse_mode="Markdown"
        )
        await callback.answer("Berhasil! Waktu grup diperpanjang 15 detik.", show_alert=True)
    else:
        await callback.answer("❌ Kamu tidak punya item Freeze! Beli di Shop menggunakan koin.", show_alert=True)

# === HANDLER PENGECEKAN JAWABAN ===
@dp.callback_query(F.data.startswith("ans_"))
async def check_answer(callback: CallbackQuery):
    msg_id = callback.message.message_id
    if msg_id not in active_games:
        return await callback.answer("Game sudah selesai!", show_alert=True)

    game = active_games[msg_id]
    current_time = time.time()

    post_game_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Main Lagi", callback_data="menu_play"),
         InlineKeyboardButton(text="🏠 Menu Utama", callback_data="menu_back")]
    ])

    if current_time > game["exp"]:
        del active_games[msg_id]
        return await callback.message.edit_caption(
            caption=f"⏰ **WAKTU HABIS!**\nJawaban yang benar: **{game['ans']}**",
            reply_markup=post_game_kb,
            parse_mode="Markdown"
        )

    user_ans = int(callback.data.split("_")[1])

    if user_ans == game["ans"]:
        del active_games[msg_id]

        durasi = current_time - game["start_time"]
        bonus_xp = 15 if durasi < 5 else (5 if durasi < 10 else 0)
        total_xp = game["xp"] + bonus_xp

        await get_or_create_player(callback.from_user.id, callback.from_user.first_name)
        await update_player_score(callback.from_user.id, total_xp, game["coins"])

        teks_menang = (
            f"🎉 **{callback.from_user.first_name} BENAR!**\n\n"
            f"Jawaban: **{game['ans']}**\n"
            f"Waktu: {durasi:.1f} detik\n\n"
            f"🎁 **+{total_xp} XP** | 🪙 **+{game['coins']} Koin**"
        )
        await callback.message.edit_caption(caption=teks_menang, reply_markup=post_game_kb, parse_mode="Markdown")
    else:
        del active_games[msg_id]
        await callback.message.edit_caption(
            caption=f"❌ **SALAH!**\n\nJawaban yang benar adalah: **{game['ans']}**",
            reply_markup=post_game_kb,
            parse_mode="Markdown"
        )

# === HANDLER LEADERBOARD ===
@dp.callback_query(F.data == "menu_rank")
async def cmd_leaderboard(callback: CallbackQuery):
    top = await get_leaderboard()

    try: await callback.message.delete()
    except: pass

    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Kembali", callback_data="menu_back")]])

    if not top:
        return await callback.message.answer("Leaderboard masih kosong!", reply_markup=kb)

    text = "📊 **TOP 5 PLAYER (XP TERTINGGI)** 📊\n\n"
    for i, p in enumerate(top, 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "👤"
        gelar = f" [{p.title}]" if p.title != "Beginner" else ""

        text += f"{medal} **{p.username}**{gelar}\n"
        text += f"   🎮 {p.xp_score} XP | ❄️ {p.freezes} | 🪙 {p.coins} Koin\n\n"

    await callback.message.answer(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

async def main():
    await init_db()
    print("🤖 Bot Heavyweight is Online (via Proxy)...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Bot berhenti: {e}")
