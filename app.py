from flask import Flask, request
import requests
import os
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading

app = Flask(__name__)

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
MI_NUMERO = os.environ.get("MI_NUMERO")

MQTT_HOST = "2772f609444f473aae9a80a4a5e31db6.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "Esp32senka"

LUCES = {
    "1": {"nombre": "Luz principal", "topic": "casa/cuarto/luz_principal"},
    "2": {"nombre": "Nube",          "topic": "casa/cuarto/nube"},
    "3": {"nombre": "Luz baño",      "topic": "casa/cuarto/luz_bano"},
    "4": {"nombre": "Luz espejo",    "topic": "casa/cuarto/luz_espejo"},
}

sesiones = {}

def publicar_mqtt(topic, mensaje):
    publish.single(
        topic, mensaje,
        hostname=MQTT_HOST, port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

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

def menu_principal():
    return (
        "🏠 *Control de mi cuarto*\n"
        "━━━━━━━━━━━━━━━\n"
        "Escribí el número de la luz:\n\n"
        "1️⃣ Luz principal\n"
        "2️⃣ Nube\n"
        "3️⃣ Luz baño\n"
        "4️⃣ Luz espejo\n\n"
        "Ejemplo: *1 on* o *2 off*"
    )

def procesar_mensaje(numero, texto):
    texto_lower = texto.lower().strip()

    # Menú principal
    if any(p in texto_lower for p in ["luces", "casa", "menu", "menú", "hola", "inicio"]):
        enviar_mensaje(numero, menu_principal())
        return

    # Comandos por número: "1 on", "2 off", etc.
    for luz_id, luz in LUCES.items():
        if texto_lower.startswith(luz_id):
            if any(p in texto_lower for p in ["on", "encend", "prend"]):
                publicar_mqtt(luz["topic"], "ON")
                enviar_mensaje(numero, f"✅ {luz['nombre']} encendida 💡")
                return
            elif any(p in texto_lower for p in ["off", "apag"]):
                publicar_mqtt(luz["topic"], "OFF")
                enviar_mensaje(numero, f"✅ {luz['nombre']} apagada 🌙")
                return
            else:
                sesiones[numero] = luz_id
                enviar_mensaje(numero, f"💡 *{luz['nombre']}*\nRespondé *on* para encender o *off* para apagar")
                return

    # Si hay sesión activa
    if numero in sesiones:
        luz_id = sesiones[numero]
        luz = LUCES[luz_id]
        if any(p in texto_lower for p in ["on", "encend", "prend"]):
            publicar_mqtt(luz["topic"], "ON")
            enviar_mensaje(numero, f"✅ {luz['nombre']} encendida 💡")
            del sesiones[numero]
            return
        elif any(p in texto_lower for p in ["off", "apag"]):
            publicar_mqtt(luz["topic"], "OFF")
            enviar_mensaje(numero, f"✅ {luz['nombre']} apagada 🌙")
            del sesiones[numero]
            return

    enviar_mensaje(numero, "Escribí *luces* para ver el menú 🏠")

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
            procesar_mensaje(numero, texto)
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())
    return "ok", 200

def mqtt_listener():
    def on_connect(c, userdata, flags, rc):
        c.subscribe("casa/cuarto/reporte")

    def on_message(c, userdata, msg):
        reporte = msg.payload.decode()
        if MI_NUMERO:
            enviar_mensaje(MI_NUMERO, reporte)

    c = mqtt.Client()
    c.username_pw_set(MQTT_USER, MQTT_PASS)
    c.tls_set()
    c.on_connect = on_connect
    c.on_message = on_message
    c.connect(MQTT_HOST, MQTT_PORT, 60)
    c.loop_forever()

threading.Thread(target=mqtt_listener, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5000, debug=True)