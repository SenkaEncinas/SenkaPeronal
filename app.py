from flask import Flask, request
import requests
import os
import paho.mqtt.publish as publish

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")

MQTT_HOST = "2772f609444f473aae9a80a4a5e31db6.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "Esp32senka"

def publicar_mqtt(topic, mensaje):
    publish.single(
        topic,
        mensaje,
        hostname=MQTT_HOST,
        port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

def procesar_mensaje(texto):
    texto = texto.lower().strip()
    if "luz" in texto and any(p in texto for p in ["on", "encend", "prend"]):
        publicar_mqtt("casa/luces", "ON")
        return "Luz encendida 💡"
    elif "luz" in texto and any(p in texto for p in ["off", "apag"]):
        publicar_mqtt("casa/luces", "OFF")
        return "Luz apagada 🌙"
    else:
        return "No entendí. Probá: 'luz on' o 'luz off'"

def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, headers=headers, json=body)

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
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = mensaje["from"]
        tipo = mensaje["type"]
        if tipo == "text":
            texto = mensaje["text"]["body"]
            respuesta = procesar_mensaje(texto)
            enviar_mensaje(numero, respuesta)
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)