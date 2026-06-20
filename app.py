from flask import Flask, request
import threading
import os
import requests
import tempfile
import paho.mqtt.client as mqtt
from whatsapp import enviar_mensaje
from comandos import procesar_mensaje
from casa import LUCES, estado_casa
from utils import transcribir_audio

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
MI_NUMERO = os.environ.get("MI_NUMERO")

MQTT_HOST = "2772f609444f473aae9a80a4a5e31db6.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "Esp32senka"

def procesar_audio(audio_id):
    try:
        headers = {"Authorization": f"Bearer {os.environ.get('WHATSAPP_TOKEN')}"}
        r = requests.get(f"https://graph.facebook.com/v21.0/{audio_id}", headers=headers)
        audio_url = r.json()["url"]
        audio_data = requests.get(audio_url, headers=headers).content
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(audio_data)
            temp_path = f.name
        texto = transcribir_audio(temp_path)
        os.remove(temp_path)
        return texto
    except Exception as e:
        print(f"Error audio: {e}")
        return None

def keep_alive():
    import urllib.request, time
    while True:
        time.sleep(600)
        try:
            urllib.request.urlopen("https://senkaperonal.onrender.com/webhook")
        except:
            pass

def mqtt_listener():
    def on_connect(c, userdata, flags, rc):
        for luz in LUCES.values():
            c.subscribe(luz["topic"])
        c.subscribe("casa/cuarto/reporte")

    def on_message(c, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        for luz_id, luz in LUCES.items():
            if topic == luz["topic"]:
                estado_casa[luz_id] = payload
        if topic == "casa/cuarto/reporte" and MI_NUMERO:
            enviar_mensaje(MI_NUMERO, payload)

    c = mqtt.Client()
    c.username_pw_set(MQTT_USER, MQTT_PASS)
    c.tls_set()
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(MQTT_HOST, MQTT_PORT, 60)
    c.loop_forever()

threading.Thread(target=keep_alive, daemon=True).start()
threading.Thread(target=mqtt_listener, daemon=True).start()

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    modo = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if modo == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.json
    try:
        entry = data.get("entry", [])
        if not entry: return "ok", 200
        changes = entry[0].get("changes", [])
        if not changes: return "ok", 200
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages: return "ok", 200
        mensaje = messages[0]
        numero = mensaje["from"]
        tipo = mensaje["type"]

        if tipo == "text":
            texto = mensaje["text"]["body"]
            respuesta = procesar_mensaje(numero, texto)
            enviar_mensaje(numero, respuesta)

        elif tipo == "audio":
            audio_id = mensaje["audio"]["id"]
            texto = procesar_audio(audio_id)
            if texto:
                enviar_mensaje(numero, f"🎤 _{texto}_")
                respuesta = procesar_mensaje(numero, texto)
                enviar_mensaje(numero, respuesta)
            else:
                enviar_mensaje(numero, "❌ No pude entender el audio.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)