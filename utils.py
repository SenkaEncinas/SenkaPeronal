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
        r = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
        data = r.json()
        bob = data["rates"].get("BOB", 6.91)
        return f"💲 *USDT:* ~1.00 USD\n💵 Equivalente: ~{bob:.2f} Bs"
    except:
        return "❌ No pude obtener el precio."

def iniciar_timer(numero, minutos, enviar_fn):
    def avisar():
        import time
        time.sleep(int(minutos) * 60)
        enviar_fn(numero, f"⏰ Timer de *{minutos} min* terminó!")
    threading.Thread(target=avisar, daemon=True).start()
    return f"⏱️ Timer de *{minutos} minutos* iniciado."