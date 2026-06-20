def obtener_usdt():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSDT", timeout=5)
        r2 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BUSDUSDT", timeout=5)
        # Usamos precio de USDT en USD directo
        precio_usd = 1.0  # USDT siempre vale ~1 USD
        # Tipo de cambio boliviano referencial
        r3 = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        data = r3.json()
        bob = data["rates"].get("BOB", 6.91)
        return f"💲 *USDT:* ~1.00 USD\n💵 Equivalente: ~{bob:.2f} Bs"
    except:
        return "❌ No pude obtener el precio."