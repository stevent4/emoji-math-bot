SHOP_ITEMS = {
    "title_jenius": {"name": "Gelar: Si Jenius 🧠", "price": 50, "type": "title"},
    "title_raja": {"name": "Gelar: Raja Hitung 👑", "price": 100, "type": "title"}
}

# Fungsi ini akan dipanggil saat user mengetik /shop
def get_shop_menu():
    text = "🛒 **EMOJI MATH SHOP** 🛒\n\nGunakan koinmu untuk membeli item:\n\n"
    for item_id, item_data in SHOP_ITEMS.items():
        text += f"- {item_data['name']} (Harga: 🪙 {item_data['price']})\n"
    text += "\nKetik `/buy [nama_item]` untuk membeli."
    return text