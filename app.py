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

def enviar_lista(numero):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "header": {"type": "text", "text": "🏠 Mi cuarto"},
            "body": {"text": "Seleccioná qué luz querés controlar:"},
            "footer": {"text": "Sistema Senka"},
            "action": {
                "button": "Ver luces",
                "sections": [{
                    "title": "Luces disponibles",
                    "rows": [
                        {"id": "1", "title": "💡 Luz principal"},
                        {"id": "2", "title": "🌟 Nube"},
                        {"id": "3", "title": "🚿 Luz baño"},
                        {"id": "4", "title": "🪞 Luz espejo"},
                    ]
                }]
            }
        }
    }
    requests.post(url, headers=headers, json=body)

def enviar_botones(numero, luz_id):
    nombre = LUCES[luz_id]["nombre"]
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {"type": "text", "text": f"💡 {nombre}"},
            "body": {"text": "¿Qué querés hacer?"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": f"{luz_id}_ON",  "title": "Encender 💡"}},
                    {"type": "reply", "reply": {"id": f"{luz_id}_OFF", "title": "Apagar 🌙"}},
                    {"type": "reply", "reply": {"id": "volver",        "title": "⬅️ Volver"}},
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=body)

def procesar_mensaje(numero, tipo, texto, interactive_id):
    texto_lower = texto.lower().strip() if texto else ""

    # Menú principal
    if any(p in texto_lower for p in ["luz", "luces", "casa", "menu", "menú", "hola", "inicio"]):
        enviar_lista(numero)
        return

    # Selección de lista
    if tipo == "interactive" and interactive_id:
        if interactive_id == "volver":
            enviar_lista(numero)
            return

        if interactive_id in LUCES:
            sesiones[numero] = interactive_id
            enviar_botones(numero, interactive_id)
            return

        if "_ON" in interactive_id or "_OFF" in interactive_id:
            partes = interactive_id.split("_")
            luz_id = partes[0]
            accion = partes[1]
            if luz_id in LUCES:
                topic = LUCES[luz_id]["topic"]
                nombre = LUCES[luz_id]["nombre"]
                publicar_mqtt(topic, accion)
                estado = "encendida 💡" if accion == "ON" else "apagada 🌙"
                enviar_mensaje(numero, f"✅ {nombre} {estado}")
                return

    # Comandos de texto directo
    for luz_id, luz in LUCES.items():
        nombre_lower = luz["nombre"].lower()
        if nombre_lower in texto_lower or f"luz {luz_id}" in texto_lower:
            if any(p in texto_lower for p in ["on", "encend", "prend"]):
                publicar_mqtt(luz["topic"], "ON")
                enviar_mensaje(numero, f"✅ {luz['nombre']} encendida 💡")
                return
            elif any(p in texto_lower for p in ["off", "apag"]):
                publicar_mqtt(luz["topic"], "OFF")
                enviar_mensaje(numero, f"✅ {luz['nombre']} apagada 🌙")
                return

    enviar_mensaje(numero, "Escribí *luces* para ver el menú de control 🏠")

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
        texto = ""
        interactive_id = ""

        if tipo == "text":
            texto = mensaje["text"]["body"]
        elif tipo == "interactive":
            inter = mensaje["interactive"]
            if inter["type"] == "list_reply":
                interactive_id = inter["list_reply"]["id"]
            elif inter["type"] == "button_reply":
                interactive_id = inter["button_reply"]["id"]

        procesar_mensaje(numero, tipo, texto, interactive_id)
    except Exception as e:
        print(f"Error: {e}")
    return "ok", 200

# MQTT listener para reportes
def mqtt_listener():
    def on_connect(client, userdata, flags, rc):
        client.subscribe("casa/cuarto/reporte")

    def on_message(client, userdata, msg):
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