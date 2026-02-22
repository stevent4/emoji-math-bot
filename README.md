# 🎮 Emoji Math PRO Bot — Adu Mekanik Otak di Telegram

**Emoji Math PRO** adalah bot Telegram interaktif yang mengubah grup obrolan biasa menjadi medan perang matematika visual. 
Cocok buat seru-seruan bareng teman grup untuk menguji kecepatan otak, ketelitian, dan pamer gelar Sultan! 🧠⚡

---

## 🚀 Fitur Utama

- 🖼️ Generate soal gambar secara *real-time* (Anti *copy-paste*)
- ⏱️ Waktu menjawab hanya 30 detik per soal
- 🔥 Sistem bonus XP untuk jawaban super cepat (<5 detik)
- 💰 Sistem ekonomi: Kumpulkan Koin dari setiap jawaban benar
- 🛒 Fitur Shop untuk membeli Gelar Eksklusif (Title)
- ❄️ Item "Freeze" untuk menambah waktu grup +15 detik
- 🚨 Panic Mode: Peringatan merah di 5 detik terakhir
- 📊 Leaderboard Global (Top 5 Player dengan XP tertinggi)
- 🔀 Soal dinamis dan *random* (Penjumlahan, Pengurangan, Perkalian)

---

## 🛡️ Fitur Admin

- 🧑‍💼 Hak akses khusus untuk Admin/Creator grup
- 🧹 Perintah `/reset_skor` untuk memulai musim baru (menghapus semua data skor)
- 🚫 Otomatis menolak eksekusi reset dari member biasa

---

## 🧪 Teknologi yang Digunakan

- 🧠 Python 3.9+
- 🤖 Aiogram 3.x (Asynchronous Telegram Bot API)
- 🎨 Pillow / PIL (Image Generation Engine)
- 🗃️ SQLAlchemy ORM + aiosqlite (Database Asynchronous)
- 📂 SQLite (Penyimpanan lokal yang ringan)

---

## 📦 Instalasi & Penggunaan

```bash
# Clone repositori
git clone https://github.com/stevent4/emoji-math-bot.git
cd emoji-math-bot

# Install semua library yang dibutuhkan
pip install aiogram sqlalchemy aiosqlite pillow

# Siapkan folder assets
# Pastikan kamu memasukkan gambar emoji (.png) dan font (.ttf) ke dalam folder ini
mkdir assets

# Masukkan TOKEN Bot Telegram kamu ke dalam file main.py
# TOKEN = "TOKEN_DARI_BOTFATHER"

# Jalankan bot
python3 main.py
```

---

## 💡 Tips BotFather

Agar bot terlihat profesional layaknya game sungguhan, atur teks profil di @BotFather.

- **Edit About:** `🧠 Adu mekanik otak di grup! Game matematika cepat tebak nilai emoji. Kumpulkan XP, beli gelar, dan rebut Top 1! ⚡`
- **Edit Description:** `Lupakan obrolan biasa, ini medan perang matematika visual! Pecahkan nilai emoji sebelum 30 detik, kumpulkan Koin, dan beli item eksklusif di Shop. Siap pecahkan rekor hari ini?`

---

## 📁 Struktur Folder Penting

- `main.py` – Otak utama bot, routing perintah, dan game loop
- `database.py` – Setup SQLAlchemy, model pemain, dan logika toko (Shop)
- `image_engine.py` – Mesin pembuat kanvas dan rendering teks ke gambar
- `assets/` – Folder wajib untuk menyimpan gambar .png transparan dan font .ttf
- `heavyweight_math.db` – File database SQLite (Terbuat otomatis)

---

## 👨‍💻 Tentang Developer

- 🌐 GitHub: [https://github.com/stevent4](https://github.com/stevent4)
- 📷 Instagram: [https://instagram.com/a.stevents](https://instagram.com/a.stevents)

---

## 📃 Lisensi

Proyek ini bersifat open-source.  
Silakan digunakan, dipelajari, dan dikembangkan sesuka hati! 🚀✨
