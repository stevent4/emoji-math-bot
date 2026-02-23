from google import genai
from google.genai import types

# Masukkan API Key Anda di sini
client = genai.Client(api_key="AIzaSyCIeE49ZR6T_NU94wOJCoDM2HTeozlDP3o")

instruction = (
    "Kamu adalah 'Emoji Math Tutor' di Telegram. Tugasmu membantu user "
    "memahami teka-teki matematika emoji. Berikan penjelasan langkah demi langkah "
    "yang mudah dipahami, ramah, dan gunakan format Markdown agar rapi. "
    "Jangan terlalu bertele-tele, langsung fokus pada cara mendapatkan nilainya."
)
async def get_gemini_response(prompt: str):
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
            )
        )
        return response.text
    except Exception as e:
        error_msg = str(e).lower()
        
        # Deteksi Error 429 (Limit API dari Google)
        if "429" in error_msg or "exhausted" in error_msg or "too many requests" in error_msg:
            
            # Cek apakah ini limit HARIAN (Quota)
            if "quota" in error_msg:
                return (
                    "🤖 **Waduh, Maaf Banget!** 😭\n"
                    "Kuota harian AI bot ini sudah habis karena terlalu banyak pemain hari ini. "
                    "Fitur AI akan aktif kembali besok siang. Tetap semangat main manual ya!"
                )
            
            # Jika bukan quota, berarti limit MENITAN (Rate Limit 5/menit)
            else:
                return (
                    "🤖 **Sabar ya Jagoan!** ⏳\n"
                    "AI sedang ngos-ngosan melayani banyak pertanyaan sekaligus. "
                    "Tunggu sekitar 1 menit lagi baru fitur AI ini bisa dipakai."
                )
                
        # Deteksi jika ada error lain (misal koneksi VPS putus)
        return f"❌ Server AI sedang gangguan kecil: {str(e)}"