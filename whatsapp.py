import requests
import os

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
BASE_URL = "https://graph.facebook.com/v21.0"

def _headers():
    return {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

def enviar_mensaje(numero, texto):
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, headers=_headers(), json=body)

def enviar_botones(numero, texto, botones):
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                    for b in botones
                ]
            }
        }
    }
    requests.post(url, headers=_headers(), json=body)

def enviar_lista(numero, texto, boton_texto, secciones):
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": texto},
            "action": {
                "button": boton_texto,
                "sections": secciones
            }
        }
    }
    requests.post(url, headers=_headers(), json=body)

# ─── Menú principal ───────────────────────────────────────────────────────────

def enviar_menu_principal(numero):
    enviar_lista(
        numero,
        "👋 *AsistentePersonal*\n¿Qué hacemos?",
        "Ver opciones",
        [
            {
                "title": "🏠 Casa",
                "rows": [
                    {"id": "menu_casa", "title": "🏠 Casa", "description": "Luces y aire del cuarto"},
                ]
            },
            {
                "title": "📋 Personal",
                "rows": [
                    {"id": "menu_agenda", "title": "📅 Agenda", "description": "Ver o crear eventos"},
                    {"id": "menu_tareas", "title": "✅ Tareas", "description": "Ver o agregar tareas"},
                ]
            },
            {
                "title": "ℹ️ Info",
                "rows": [
                    {"id": "menu_clima", "title": "🌤️ Clima", "description": "Clima de Santa Cruz"},
                    {"id": "menu_usdt",  "title": "💵 USDT",  "description": "Precio Binance P2P Bolivia"},
                ]
            }
        ]
    )

# ─── Menú casa ────────────────────────────────────────────────────────────────

def enviar_menu_casa(numero):
    enviar_botones(
        numero,
        "🏠 *Control del cuarto*\n¿Qué querés controlar?",
        [
            {"id": "menu_luces", "title": "💡 Luces"},
            {"id": "menu_aire",  "title": "❄️ Aire"},
            {"id": "volver_principal", "title": "⬅️ Volver"},
        ]
    )

# ─── Menú luces ───────────────────────────────────────────────────────────────
def enviar_menu_luces(numero):
    enviar_lista(
        numero,
        "💡 *Control de luces*\n¿Qué querés hacer?\n\n_Escribí *casa* para volver atrás_",
        "Ver luces",
        [
            {
                "title": "💡 Encender",
                "rows": [
                    {"id": "luz_on_1",   "title": "💡 Luz principal"},
                    {"id": "luz_on_2",   "title": "💡 Nube"},
                    {"id": "luz_on_3",   "title": "💡 Luz baño"},
                    {"id": "luz_on_4",   "title": "💡 Luz espejo"},
                    {"id": "luz_on_all", "title": "💡 Todas ON"},
                ]
            },
            {
                "title": "🌙 Apagar",
                "rows": [
                    {"id": "luz_off_1",   "title": "🌙 Luz principal"},
                    {"id": "luz_off_2",   "title": "🌙 Nube"},
                    {"id": "luz_off_3",   "title": "🌙 Luz baño"},
                    {"id": "luz_off_4",   "title": "🌙 Luz espejo"},
                    {"id": "luz_off_all", "title": "🌙 Todas OFF"},
                ]
            }
        ]
    )

# ─── Menú aire ────────────────────────────────────────────────────────────────

def enviar_menu_aire(numero):
    enviar_botones(
        numero,
        "❄️ *Aire acondicionado*\n¿Qué hacemos?",
        [
            {"id": "aire_on",     "title": "❄️ Encender"},
            {"id": "aire_off",    "title": "🌙 Apagar"},
            {"id": "volver_casa", "title": "⬅️ Volver"},
        ]
    )

# ─── Botones fecha (crear evento) ─────────────────────────────────────────────

def enviar_botones_fecha(numero):
    enviar_botones(
        numero,
        "📅 ¿Para qué día es el evento?",
        [
            {"id": "fecha_hoy",    "title": "📅 Hoy"},
            {"id": "fecha_manana", "title": "📅 Mañana"},
            {"id": "fecha_manual", "title": "✏️ Otra fecha"},
        ]
    )

# ─── Lista de horas (crear evento) ────────────────────────────────────────────
def enviar_lista_horas(numero):
    enviar_lista(
        numero,
        "🕐 ¿A qué hora?\n\n_O escribí la hora directamente: *15:00* o *3 tarde*_",
        "Ver horarios",
        [
            {
                "title": "🌅 Mañana",
                "rows": [
                    {"id": "hora_7",  "title": "7:00"},
                    {"id": "hora_8",  "title": "8:00"},
                    {"id": "hora_9",  "title": "9:00"},
                    {"id": "hora_10", "title": "10:00"},
                ]
            },
            {
                "title": "☀️ Tarde",
                "rows": [
                    {"id": "hora_12", "title": "12:00"},
                    {"id": "hora_14", "title": "14:00"},
                    {"id": "hora_16", "title": "16:00"},
                    {"id": "hora_18", "title": "18:00"},
                ]
            },
            {
                "title": "🌙 Noche",
                "rows": [
                    {"id": "hora_20", "title": "20:00"},
                    {"id": "hora_22", "title": "22:00"},
                ]
            }
        ]
    )
def enviar_imagen_bytes(numero, imagen_bytes, caption=""):
    import base64
    url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
    # Subir la imagen primero como media
    upload_url = f"{BASE_URL}/{PHONE_NUMBER_ID}/media"
    files = {
        "file": ("qr.png", base64.b64decode(imagen_bytes), "image/png"),
        "messaging_product": (None, "whatsapp")
    }
    r = requests.post(upload_url, headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}, files=files)
    media_id = r.json().get("id")
    if not media_id:
        return

    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "image",
        "image": {"id": media_id, "caption": caption}
    }
    requests.post(url, headers=_headers(), json=body)
def enviar_imagen_qr(numero, qr_bytes_base64, caption=""):
    import base64 as b64
    try:
        # Subir imagen a WhatsApp
        upload_url = f"{BASE_URL}/{PHONE_NUMBER_ID}/media"
        imagen = b64.b64decode(qr_bytes_base64)
        files = {
            "file": ("qr.png", imagen, "image/png"),
            "messaging_product": (None, "whatsapp")
        }
        r = requests.post(
            upload_url,
            headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"},
            files=files
        )
        media_id = r.json().get("id")
        if not media_id:
            return

        # Enviar imagen
        url = f"{BASE_URL}/{PHONE_NUMBER_ID}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "image",
            "image": {"id": media_id, "caption": caption}
        }
        requests.post(url, headers=_headers(), json=body)
    except Exception as e:
        print(f"Error enviando QR: {e}")