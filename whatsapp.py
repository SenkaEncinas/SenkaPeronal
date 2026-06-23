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
        "💡 *Control de luces*\n¿Qué querés hacer?",
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
            },
            {
                "title": "↩️ Navegación",
                "rows": [
                    {"id": "volver_casa", "title": "⬅️ Volver a Casa"},
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
        "🕐 ¿A qué hora?",
        "Ver horarios",
        [
            {
                "title": "🌅 Mañana",
                "rows": [
                    {"id": "hora_8",  "title": "8:00"},
                    {"id": "hora_9",  "title": "9:00"},
                    {"id": "hora_10", "title": "10:00"},
                    {"id": "hora_11", "title": "11:00"},
                ]
            },
            {
                "title": "☀️ Tarde",
                "rows": [
                    {"id": "hora_12", "title": "12:00"},
                    {"id": "hora_13", "title": "13:00"},
                    {"id": "hora_14", "title": "14:00"},
                    {"id": "hora_15", "title": "15:00"},
                    {"id": "hora_16", "title": "16:00"},
                    {"id": "hora_17", "title": "17:00"},
                ]
            },
            {
                "title": "🌙 Noche",
                "rows": [
                    {"id": "hora_18",     "title": "18:00"},
                    {"id": "hora_19",     "title": "19:00"},
                    {"id": "hora_20",     "title": "20:00"},
                    {"id": "hora_21",     "title": "21:00"},
                    {"id": "hora_manual", "title": "✏️ Otra hora"},
                ]
            }
        ]
    )