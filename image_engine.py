from PIL import Image, ImageDraw, ImageFont
import io

def generate_math_image(e1_path, e2_path, val1, val2, info_op, tanya_op):
    # Buat kanvas abu-abu gelap
    bg_color = (40, 44, 52)
    img = Image.new('RGB', (500, 400), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Coba muat font, jika gagal pakai default
    try:
        font = ImageFont.truetype("assets/game_font.ttf", 40)
        font_small = ImageFont.truetype("assets/game_font.ttf", 25)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Muat gambar emoji
    try:
        e1 = Image.open(e1_path).resize((60, 60)).convert("RGBA")
        e2 = Image.open(e2_path).resize((60, 60)).convert("RGBA")
    except Exception as e:
        print(f"Error muat gambar: {e}. Pastikan file ada di folder assets/")
        e1 = Image.new('RGBA', (60, 60), color='red')
        e2 = Image.new('RGBA', (60, 60), color='blue')

    # Hitung nilai info baris kedua
    if info_op == '+': info_val = val1 + val2
    elif info_op == '-': info_val = val1 - val2
    else: info_val = val1 * val2

    # --- MENGGAMBAR KE KANVAS ---
    # Baris 1: E1 + E1 = Hasil
    img.paste(e1, (50, 40), e1)
    draw.text((120, 50), "+", fill="white", font=font)
    img.paste(e1, (170, 40), e1)
    draw.text((250, 50), f"= {val1 + val1}", fill="white", font=font)

    # Baris 2: E1 (op) E2 = Hasil
    img.paste(e1, (50, 140), e1)
    draw.text((120, 150), info_op, fill="white", font=font)
    img.paste(e2, (170, 140), e2)
    draw.text((250, 150), f"= {info_val}", fill="white", font=font)

    # Baris 3: Pertanyaan
    draw.text((50, 240), "BERAPA HASIL DARI:", fill="yellow", font=font_small)
    img.paste(e1, (50, 290), e1)
    draw.text((120, 300), tanya_op, fill="white", font=font)
    img.paste(e2, (170, 290), e2)
    draw.text((250, 300), "= ???", fill="#FF5555", font=font)

    # Simpan gambar ke memori sementara (bukan hardisk)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr