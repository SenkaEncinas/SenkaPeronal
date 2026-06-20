import requests
import threading

def obtener_clima():
    try:
        r = requests.get("https://wttr.in/Santa+Cruz+de+la+Sierra+Bolivia?format=3&m", timeout=5)
        return f"🌤️ {r.text.strip()}"
    except:
        return "❌ No pude obtener el clima."

def obtener_usdt():
    try:
        url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
        headers = {"Content-Type": "application/json"}
        body = {
            "asset": "USDT",
            "fiat": "BOB",
            "merchantCheck": False,
            "page": 1,
            "payTypes": [],
            "publisherType": None,
            "rows": 5,
            "tradeType": "BUY"
        }
        r = requests.post(url, headers=headers, json=body, timeout=10)
        data = r.json()
        precios = [float(ad["adv"]["price"]) for ad in data["data"]]
        promedio = sum(precios) / len(precios)
        minimo = min(precios)
        maximo = max(precios)
        return (
            f"💲 *USDT/BOB — Binance P2P*\n"
            f"━━━━━━━━━━━━━\n"
            f"📊 Promedio: *{promedio:.2f} Bs*\n"
            f"⬇️ Mínimo: *{minimo:.2f} Bs*\n"
            f"⬆️ Máximo: *{maximo:.2f} Bs*\n"
            f"_(Top 5 ofertas de compra)_"
        )
    except Exception as e:
        return f"❌ No pude obtener el precio P2P: {e}"

def iniciar_timer(numero, minutos, enviar_fn):
    def avisar():
        import time
        time.sleep(int(minutos) * 60)
        enviar_fn(numero, f"⏰ Timer de *{minutos} min* terminó!")
    threading.Thread(target=avisar, daemon=True).start()
    return f"⏱️ Timer de *{minutos} minutos* iniciado."