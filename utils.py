import requests
import threading
import os
from groq import Groq

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def obtener_clima():
    try:
        # Datos detallados
        r = requests.get(
            "https://wttr.in/Santa+Cruz+de+la+Sierra+Bolivia?format=j1",
            timeout=5
        )
        data = r.json()
        
        hoy = data["weather"][0]
        actual = data["current_condition"][0]
        
        temp_actual = actual["temp_C"]
        sensacion = actual["FeelsLikeC"]
        humedad = actual["humidity"]
        desc = actual["lang_es"][0]["value"] if actual.get("lang_es") else actual["weatherDesc"][0]["value"]
        
        temp_max = hoy["maxtempC"]
        temp_min = hoy["mintempC"]
        lluvia = hoy["hourly"][4]["chanceofrain"]  # probabilidad al mediodía
        nieve = hoy["hourly"][4]["chanceofsunshine"]
        viento = actual["windspeedKmph"]
        
        # Emoji según condición
        if int(lluvia) > 60:
            emoji_dia = "🌧️ Va a llover bastante"
            consejo = "☂️ Llevá paraguas"
        elif int(lluvia) > 30:
            emoji_dia = "🌦️ Puede llover"
            consejo = "👀 Ojo con la lluvia"
        elif int(temp_max) > 32:
            emoji_dia = "☀️ Día caluroso"
            consejo = "💧 Tomá bastante agua"
        elif int(temp_max) < 22:
            emoji_dia = "🧥 Día fresco"
            consejo = "🧣 Considerá abrigarte"
        else:
            emoji_dia = "🌤️ Día agradable"
            consejo = "😎 Buen día para salir"

        return (
            f"🌡️ *Clima — Santa Cruz*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{emoji_dia}\n"
            f"📍 Ahora: *{temp_actual}°C* — {desc}\n"
            f"🌡️ Máx: *{temp_max}°C* / Mín: *{temp_min}°C*\n"
            f"💧 Humedad: *{humedad}%*\n"
            f"🌧️ Prob. lluvia: *{lluvia}%*\n"
            f"💨 Viento: *{viento} km/h*\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{consejo}"
        )
    except Exception as e:
        return f"❌ No pude obtener el clima: {e}"
    
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

def transcribir_audio(audio_path):
    try:
        with open(audio_path, "rb") as f:
            transcripcion = groq_client.audio.transcriptions.create(
                file=(audio_path, f.read()),
                model="whisper-large-v3",
                language="es"
            )
        return transcripcion.text
    except Exception as e:
        return None