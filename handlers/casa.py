import paho.mqtt.publish as publish

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

estado_casa = {"1": "OFF", "2": "OFF", "3": "OFF", "4": "OFF"}

MAPA_LUCES = {
    "1": ["principal", "techo"],
    "2": ["nube"],
    "3": ["baño", "bano"],
    "4": ["espejo"]
}

def publicar(topic, mensaje):
    publish.single(
        topic, mensaje,
        hostname=MQTT_HOST, port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

def encender(luz_id):
    publicar(LUCES[luz_id]["topic"], "ON")
    estado_casa[luz_id] = "ON"
    return f"💡 {LUCES[luz_id]['nombre']} encendida"

def apagar(luz_id):
    publicar(LUCES[luz_id]["topic"], "OFF")
    estado_casa[luz_id] = "OFF"
    return f"🌙 {LUCES[luz_id]['nombre']} apagada"

def todo_on():
    for k in LUCES:
        publicar(LUCES[k]["topic"], "ON")
        estado_casa[k] = "ON"
    return "💡 Todas las luces encendidas"

def todo_off():
    for k in LUCES:
        publicar(LUCES[k]["topic"], "OFF")
        estado_casa[k] = "OFF"
    return "🌙 Todas las luces apagadas"

def get_estado():
    resp = "🏠 *Estado:*\n━━━━━━━━━━━━━\n"
    for k, v in estado_casa.items():
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
def aire_on():
    publicar("casa/cuarto/aire", "ON")
    return "❄️ Aire encendido"

def aire_off():
    publicar("casa/cuarto/aire", "OFF")
    return "🌙 Aire apagado"