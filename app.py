from flask import Flask, request
import requests
import os
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz

app = Flask(__name__)

# WhatsApp
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
MI_NUMERO = os.environ.get("MI_NUMERO")

# MQTT
MQTT_HOST = "2772f609444f473aae9a80a4a5e31db6.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "esp32"
MQTT_PASS = "Esp32senka"

# Firebase
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Zona horaria Bolivia
BOL = pytz.timezone("America/La_Paz")

# Luces
LUCES = {
    "1": {"nombre": "Luz principal", "topic": "casa/cuarto/luz_principal"},
    "2": {"nombre": "Nube",          "topic": "casa/cuarto/nube"},
    "3": {"nombre": "Luz baño",      "topic": "casa/cuarto/luz_bano"},
    "4": {"nombre": "Luz espejo",    "topic": "casa/cuarto/luz_espejo"},
}

estado_casa = {"1": "OFF", "2": "OFF", "3": "OFF", "4": "OFF"}
sesiones = {}

# ─── MQTT ───────────────────────────────────────────────
def publicar_mqtt(topic, mensaje):
    publish.single(
        topic, mensaje,
        hostname=MQTT_HOST, port=MQTT_PORT,
        auth={"username": MQTT_USER, "password": MQTT_PASS},
        tls={}
    )

# ─── WHATSAPP ───────────────────────────────────────────
def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
    body = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": texto}}
    requests.post(url, headers=headers, json=body)

# ─── MENÚS ──────────────────────────────────────────────
def menu_principal():
    return (
        "🏠 *AsistentePersonal — Menú*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 *luces* — Control de luces\n"
        "📝 *nota [texto]* — Guardar nota\n"
        "📋 *notas* — Ver mis notas\n"
        "✅ *tarea [texto]* — Agregar tarea\n"
        "📌 *tareas* — Ver tareas pendientes\n"
        "✔️ *hecho [número]* — Marcar tarea lista\n"
        "💰 *gasto [monto] [descripción]* — Registrar gasto\n"
        "💵 *gastos* — Ver gastos del mes\n"
        "👤 *contacto [nombre]* — Ver info de contacto\n"
        "⏱️ *timer [minutos]* — Iniciar temporizador\n"
        "🌤️ *clima* — Clima en Santa Cruz\n"
        "💲 *usdt* — Precio del dólar/USDT\n"
        "🏠 *estado* — Estado de las luces\n"
        "🌙 *buenas noches* — Apagar todo\n"
        "☀️ *buenos días* — Rutina de mañana\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

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

# ─── FUNCIONES ──────────────────────────────────────────
def guardar_nota(numero, texto):
    db.collection("notas").add({
        "numero": numero,
        "texto": texto,
        "fecha": datetime.now(BOL).isoformat()
    })
    return f"📝 Nota guardada: _{texto}_"

def ver_notas(numero):
    docs = db.collection("notas").where("numero", "==", numero).limit(10).stream()
    notas = list(docs)
    if not notas:
        return "📝 No tenés notas guardadas."
    resp = "📋 *Tus notas:*\n━━━━━━━━━━━━━\n"
    for i, doc in enumerate(notas, 1):
        d = doc.to_dict()
        resp += f"{i}. {d['texto']}\n"
    return resp

def agregar_tarea(numero, texto):
    db.collection("tareas").add({
        "numero": numero,
        "texto": texto,
        "hecho": False,
        "fecha": datetime.now(BOL).isoformat()
    })
    return f"✅ Tarea agregada: _{texto}_"

def ver_tareas(numero):
    docs = db.collection("tareas").where("numero", "==", numero).where("hecho", "==", False).limit(10).stream()
    tareas = list(docs)
    if not tareas:
        return "✅ No tenés tareas pendientes."
    resp = "📌 *Tareas pendientes:*\n━━━━━━━━━━━━━\n"
    for i, doc in enumerate(tareas, 1):
        d = doc.to_dict()
        resp += f"{i}. {d['texto']}\n"
    return resp

def marcar_hecho(numero, indice):
    docs = list(db.collection("tareas").where("numero", "==", numero).where("hecho", "==", False).limit(10).stream())
    if indice < 1 or indice > len(docs):
        return "❌ Número de tarea inválido."
    doc = docs[indice - 1]
    doc.reference.update({"hecho": True})
    return f"✔️ Tarea completada: _{doc.to_dict()['texto']}_"

def registrar_gasto(numero, monto, descripcion):
    db.collection("gastos").add({
        "numero": numero,
        "monto": float(monto),
        "descripcion": descripcion,
        "fecha": datetime.now(BOL).isoformat(),
        "mes": datetime.now(BOL).strftime("%Y-%m")
    })
    return f"💰 Gasto registrado: *{monto} Bs* — {descripcion}"

def ver_gastos(numero):
    mes_actual = datetime.now(BOL).strftime("%Y-%m")
    docs = db.collection("gastos").where("numero", "==", numero).where("mes", "==", mes_actual).limit(50).stream()
    gastos = list(docs)
    if not gastos:
        return "💵 No tenés gastos registrados este mes."
    total = 0
    resp = f"💰 *Gastos de {mes_actual}:*\n━━━━━━━━━━━━━\n"
    for doc in gastos:
        d = doc.to_dict()
        resp += f"• {d['descripcion']}: *{d['monto']} Bs*\n"
        total += d['monto']
    resp += f"━━━━━━━━━━━━━\n*Total: {total} Bs*"
    return resp

def ver_contacto(nombre):
    docs = db.collection("contactos").where("nombre", "==", nombre.lower()).limit(1).stream()
    contactos = list(docs)
    if not contactos:
        return f"👤 No encontré el contacto _{nombre}_."
    d = contactos[0].to_dict()
    resp = f"👤 *{d.get('nombre', '').title()}*\n━━━━━━━━━━━━━\n"
    for k, v in d.items():
        if k != "nombre":
            resp += f"• {k}: {v}\n"
    return resp

def estado_luces():
    nombres = {"1": "Luz principal", "2": "Nube", "3": "Luz baño", "4": "Luz espejo"}
    resp = "🏠 *Estado de las luces:*\n━━━━━━━━━━━━━\n"
    for k, v in estado_casa.items():
        icono = "💡" if v == "ON" else "🌙"
        resp += f"{icono} {nombres[k]}: *{v}*\n"
    return resp

def obtener_clima():
    try:
        r = requests.get("https://wttr.in/Santa+Cruz+de+la+Sierra+Bolivia?format=3", timeout=5)
        return f"🌤️ {r.text.strip()}"
    except:
        return "❌ No pude obtener el clima."

def obtener_usdt():
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTUSDT", timeout=5)
        r2 = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTARS", timeout=5)
        ars = float(r2.json()["price"])
        return f"💲 *USDT/ARS:* {ars:.2f}\n💵 Referencial Bolivia: ~{ars*0.145:.2f} Bs"
    except:
        return "❌ No pude obtener el precio."

def iniciar_timer(numero, minutos):
    def avisar():
        import time
        time.sleep(int(minutos) * 60)
        enviar_mensaje(numero, f"⏰ ¡Tiempo! Tu timer de *{minutos} minutos* terminó.")
    threading.Thread(target=avisar, daemon=True).start()
    return f"⏱️ Timer de *{minutos} minutos* iniciado. Te aviso cuando termine."

def buenas_noches():
    for luz in LUCES.values():
        publicar_mqtt(luz["topic"], "OFF")
    for k in estado_casa:
        estado_casa[k] = "OFF"
    return "🌙 *Buenas noches!*\nTodas las luces apagadas. Que descanses 😴"

def buenos_dias():
    publicar_mqtt(LUCES["1"]["topic"], "ON")
    estado_casa["1"] = "ON"
    return "☀️ *Buenos días!*\nLuz principal encendida. Que tengas un excelente día 💪"

# ─── PROCESADOR ─────────────────────────────────────────
def procesar_mensaje(numero, texto):
    t = texto.lower().strip()

    if t in ["menu", "menú", "hola", "inicio", "ayuda", "help"]:
        return menu_principal()

    if t in ["luces", "luz"]:
        return menu_luces()

    if t == "todo on":
        for luz in LUCES.values():
            publicar_mqtt(luz["topic"], "ON")
        for k in estado_casa: estado_casa[k] = "ON"
        return "💡 Todas las luces encendidas"

    if t == "todo off":
        for luz in LUCES.values():
            publicar_mqtt(luz["topic"], "OFF")
        for k in estado_casa: estado_casa[k] = "OFF"
        return "🌙 Todas las luces apagadas"

    for luz_id, luz in LUCES.items():
        if t.startswith(luz_id + " "):
            if any(p in t for p in ["on", "encend", "prend"]):
                publicar_mqtt(luz["topic"], "ON")
                estado_casa[luz_id] = "ON"
                return f"💡 {luz['nombre']} encendida"
            elif any(p in t for p in ["off", "apag"]):
                publicar_mqtt(luz["topic"], "OFF")
                estado_casa[luz_id] = "OFF"
                return f"🌙 {luz['nombre']} apagada"

    if t == "estado":
        return estado_luces()

    if t.startswith("nota "):
        return guardar_nota(numero, texto[5:])
    if t == "notas":
        return ver_notas(numero)

    if t.startswith("tarea "):
        return agregar_tarea(numero, texto[6:])
    if t == "tareas":
        return ver_tareas(numero)
    if t.startswith("hecho "):
        try:
            return marcar_hecho(numero, int(t.split()[1]))
        except:
            return "❌ Usá: *hecho [número]*"

    if t.startswith("gasto "):
        try:
            partes = texto.split(" ", 2)
            return registrar_gasto(numero, partes[1], partes[2] if len(partes) > 2 else "sin descripción")
        except:
            return "❌ Usá: *gasto [monto] [descripción]*"
    if t == "gastos":
        return ver_gastos(numero)

    if t.startswith("contacto "):
        return ver_contacto(texto[9:])

    if t.startswith("timer "):
        try:
            return iniciar_timer(numero, t.split()[1])
        except:
            return "❌ Usá: *timer [minutos]*"

    if t == "clima":
        return obtener_clima()

    if t in ["usdt", "dolar", "dólar"]:
        return obtener_usdt()

    if "buenas noches" in t:
        return buenas_noches()
    if "buenos días" in t or "buenos dias" in t:
        return buenos_dias()

    return "No entendí. Escribí *menu* para ver las opciones 🏠"

# ─── WEBHOOK ────────────────────────────────────────────
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
        if not entry:
            return "ok", 200
        changes = entry[0].get("changes", [])
        if not changes:
            return "ok", 200
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "ok", 200
        mensaje = messages[0]
        numero = mensaje["from"]
        tipo = mensaje["type"]
        if tipo == "text":
            texto = mensaje["text"]["body"]
            respuesta = procesar_mensaje(numero, texto)
            enviar_mensaje(numero, respuesta)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
    return "ok", 200

# ─── MQTT LISTENER ──────────────────────────────────────
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

threading.Thread(target=mqtt_listener, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5000, debug=True)