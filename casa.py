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

def publicar_mqtt(topic, mensaje):
    publish.single(
        topic, mensaje,
        hostname=MQTT_HOST, port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

def encender(luz_id):
    publicar_mqtt(LUCES[luz_id]["topic"], "ON")
    estado_casa[luz_id] = "ON"
    return f"💡 {LUCES[luz_id]['nombre']} encendida"

def apagar(luz_id):
    publicar_mqtt(LUCES[luz_id]["topic"], "OFF")
    estado_casa[luz_id] = "OFF"
    return f"🌙 {LUCES[luz_id]['nombre']} apagada"

def todo_on():
    for k in LUCES:
        publicar_mqtt(LUCES[k]["topic"], "ON")
        estado_casa[k] = "ON"
    return "💡 Todas las luces encendidas"

def todo_off():
    for k in LUCES:
        publicar_mqtt(LUCES[k]["topic"], "OFF")
        estado_casa[k] = "OFF"
    return "🌙 Todas las luces apagadas"

def get_estado():
    nombres = {"1": "Luz principal", "2": "Nube", "3": "Luz baño", "4": "Luz espejo"}
    resp = "🏠 *Estado:*\n━━━━━━━━━━━━━\n"
    for k, v in estado_casa.items():
        icono = "💡" if v == "ON" else "🌙"
        resp += f"{icono} {nombres[k]}: *{v}*\n"
    return resp

def menu_luces():
    return (
        "💡 *Control de luces*\n"
        "━━━━━━━━━━━━━━━\n"
        "1️⃣ Luz principal\n"
        "2️⃣ Nube\n"
        "3️⃣ Luz baño\n"
        "4️⃣ Luz espejo\n\n"
        "Ejemplos:\n"
        "*1 on* — encender luz principal\n"
        "*2 off* — apagar nube\n"
        "*todo on* — encender todo\n"
        "*todo off* — apagar todo"
    )

def buenas_noches():
    todo_off()
    return "🌙 *Buenas noches!* Todas las luces apagadas 😴"

def buenos_dias():
    encender("1")
    return "☀️ *Buenos días!* Luz principal encendida 💪"