import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import threading
import json
import os

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

TOPIC_A_ID = {v["topic"]: k for k, v in LUCES.items()}

MAPA_LUCES = {
    "1": ["principal", "techo"],
    "2": ["nube"],
    "3": ["baño", "bano"],
    "4": ["espejo"]
}

ESTADO_FILE = "/tmp/estado_casa.json"

def leer_estado():
    if os.path.exists(ESTADO_FILE):
        with open(ESTADO_FILE, "r") as f:
            return json.load(f)
    return {"1": "OFF", "2": "OFF", "3": "OFF", "4": "OFF"}

def guardar_estado(estado):
    with open(ESTADO_FILE, "w") as f:
        json.dump(estado, f)

# ─── Cliente MQTT persistente ─────────────────────────────────────────────────

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for luz in LUCES.values():
            client.subscribe(luz["topic"])
        print("MQTT listener conectado")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    if topic in TOPIC_A_ID:
        luz_id = TOPIC_A_ID[topic]
        if payload in ("ON", "OFF"):
            estado = leer_estado()
            estado[luz_id] = payload
            guardar_estado(estado)
            print(f"[MQTT] {LUCES[luz_id]['nombre']} → {payload}")

def iniciar_listener():
    listener = mqtt.Client(client_id="flask_listener")
    listener.username_pw_set(MQTT_USER, MQTT_PASS)
    listener.tls_set()
    listener.on_connect = on_connect
    listener.on_message = on_message
    try:
        listener.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        listener.loop_forever()
    except Exception as e:
        print(f"MQTT listener error: {e}")

_thread = threading.Thread(target=iniciar_listener, daemon=True)
_thread.start()

# ─── Publicar comandos ────────────────────────────────────────────────────────

def publicar(topic, mensaje):
    publish.single(
        topic, mensaje,
        hostname=MQTT_HOST, port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

# ─── Funciones de control ─────────────────────────────────────────────────────

def encender(luz_id):
    publicar(LUCES[luz_id]["topic"], "ON")
    estado = leer_estado()
    estado[luz_id] = "ON"
    guardar_estado(estado)
    return f"💡 {LUCES[luz_id]['nombre']} encendida"

def apagar(luz_id):
    publicar(LUCES[luz_id]["topic"], "OFF")
    estado = leer_estado()
    estado[luz_id] = "OFF"
    guardar_estado(estado)
    return f"🌙 {LUCES[luz_id]['nombre']} apagada"

def todo_on():
    estado = leer_estado()
    for k in LUCES:
        publicar(LUCES[k]["topic"], "ON")
        estado[k] = "ON"
    guardar_estado(estado)
    return "💡 Todas las luces encendidas"

def todo_off():
    estado = leer_estado()
    for k in LUCES:
        publicar(LUCES[k]["topic"], "OFF")
        estado[k] = "OFF"
    guardar_estado(estado)
    return "🌙 Todas las luces apagadas"

def get_estado():
    estado = leer_estado()
    resp = "🏠 *Estado:*\n━━━━━━━━━━━━━\n"
    for k, v in estado.items():
        icono = "💡" if v == "ON" else "🌙"
        resp += f"{icono} {LUCES[k]['nombre']}: *{v}*\n"
    return resp

def menu():
    return (
        "💡 *Control de luces*\n"
        "━━━━━━━━━━━━━━━\n"
        "1️⃣ Luz principal\n"
        "2️⃣ Nube\n"
        "3️⃣ Luz baño\n"
        "4️⃣ Luz espejo\n\n"
        "Ejemplos:\n"
        "*encendé la principal*\n"
        "*apagá la nube*\n"
        "*todo on* / *todo off*"
    )

def buenas_noches():
    todo_off()
    return "🌙 Todas las luces apagadas 😴"

def buenos_dias():
    encender("1")
    return "☀️ Luz principal encendida 💪"

def procesar(t):
    if any(p in t for p in ["todo", "todas"]) and any(p in t for p in ["on", "encend", "prend"]):
        return todo_on()
    if any(p in t for p in ["todo", "todas"]) and any(p in t for p in ["off", "apag"]):
        return todo_off()
    for luz_id, palabras in MAPA_LUCES.items():
        if any(p in t for p in palabras):
            if any(p in t for p in ["on", "encend", "prend", "pone"]):
                return encender(luz_id)
            elif any(p in t for p in ["off", "apag", "sac"]):
                return apagar(luz_id)
    for luz_id in LUCES:
        if t.startswith(luz_id + " "):
            if any(p in t for p in ["on", "encend", "prend"]):
                return encender(luz_id)
            elif any(p in t for p in ["off", "apag"]):
                return apagar(luz_id)
    return menu()