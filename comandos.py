from casa import LUCES, encender, apagar, todo_on, todo_off, get_estado, menu_luces, buenas_noches, buenos_dias
from google_api import ver_eventos_hoy, crear_evento, ver_tasks, agregar_task, get_services
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import enviar_mensaje
from datetime import datetime, timedelta
import pytz

BOL = pytz.timezone("America/La_Paz")

def menu_principal():
    return (
        "🏠 *AsistentePersonal*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 *luces* — Control de luces\n"
        "📅 *agenda* — Ver eventos de hoy\n"
        "📅 *evento [titulo] [hoy/mañana] [HH:MM]*\n"
        "✅ *tareas* — Ver Google Tasks\n"
        "✅ *tarea [texto]* — Agregar tarea\n"
        "⏱️ *timer [minutos]* — Temporizador\n"
        "🌤️ *clima* — Clima Santa Cruz\n"
        "💲 *usdt* — Precio USDT\n"
        "🏠 *estado* — Estado luces\n"
        "🌙 *bn* — Buenas noches\n"
        "☀️ *bd* — Buenos días\n"
        "━━━━━━━━━━━━━━━━━━━"
    )

def get_agenda_manana():
    try:
        calendar, _ = get_services()
        manana_inicio = (datetime.now(BOL) + timedelta(days=1)).replace(hour=0, minute=0, second=0).isoformat()
        manana_fin = (datetime.now(BOL) + timedelta(days=1)).replace(hour=23, minute=59, second=59).isoformat()
        eventos = calendar.events().list(
            calendarId='primary',
            timeMin=manana_inicio,
            timeMax=manana_fin,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        if not eventos:
            return "📅 No tenés eventos mañana."
        resp = "📅 *Eventos de mañana:*\n━━━━━━━━━━━━━\n"
        for e in eventos:
            inicio = e['start'].get('dateTime', e['start'].get('date'))
            hora = datetime.fromisoformat(inicio).strftime('%H:%M') if 'T' in inicio else "Todo el día"
            resp += f"🕐 {hora} — {e['summary']}\n"
        return resp
    except:
        return "📅 No pude obtener eventos de mañana."

def procesar_mensaje(numero, texto):
    t = texto.lower().strip()

    # Menú
    if any(p in t for p in ["menu", "menú", "ayuda", "help", "inicio"]):
        return menu_principal()

    # Saludo
    if any(p in t for p in ["hola", "buenas", "hey", "qué tal", "como estas"]):
        return menu_principal()

    # Luces
    if any(p in t for p in ["luces", "luz", "focos", "foco"]) and not any(p in t for p in ["on", "off", "encend", "apag", "prend"]):
        return menu_luces()

    # Todo on/off
    if any(p in t for p in ["todo", "todas", "todos"]) and any(p in t for p in ["on", "encend", "prend"]):
        return todo_on()
    if any(p in t for p in ["todo", "todas", "todos"]) and any(p in t for p in ["off", "apag"]):
        return todo_off()

    # Luces individuales
    for luz_id, luz in LUCES.items():
        nombre = luz["nombre"].lower()
        palabras = nombre.split()
        if any(p in t for p in palabras) or luz_id in t:
            if any(p in t for p in ["on", "encend", "prend", "pone"]):
                return encender(luz_id)
            elif any(p in t for p in ["off", "apag", "sac"]):
                return apagar(luz_id)

    # Estado
    if any(p in t for p in ["estado", "qué luces", "que luces", "cuales", "cuáles"]):
        return get_estado()

    # Agenda / Calendar
    if any(p in t for p in ["agenda", "eventos", "calendario", "qué tengo", "que tengo"]) and not any(p in t for p in ["mañana", "manana"]):
        return ver_eventos_hoy()

    # Crear evento
    if any(p in t for p in ["agenda", "agendar", "crear evento", "nuevo evento", "reunión", "reunion"]) and any(p in t for p in ["hoy", "mañana", "manana"]):
        try:
            partes = texto.split(" ", 3)
            return crear_evento(partes[1], partes[2], partes[3])
        except:
            return "❌ Usá: *evento [titulo] [hoy/mañana] [HH:MM]*"

    # Tareas
    if any(p in t for p in ["tareas", "pendientes", "qué tengo pendiente", "que tengo pendiente"]):
        return ver_tasks()
    if any(p in t for p in ["agregar tarea", "nueva tarea", "añadir tarea", "tarea "]):
        return agregar_task(texto.split("tarea ", 1)[-1])

    # Timer
    if any(p in t for p in ["timer", "temporizador", "alarma", "minutos", "tiempo"]):
        try:
            nums = [s for s in t.split() if s.isdigit()]
            if nums:
                return iniciar_timer(numero, nums[0], enviar_mensaje)
        except:
            pass
        return "❌ Usá: *timer [minutos]*"

    # Clima
    if any(p in t for p in ["clima", "tiempo", "temperatura", "lluvia", "calor", "frio", "frío"]):
        return obtener_clima()

    # USDT
    if any(p in t for p in ["usdt", "dolar", "dólar", "precio", "cambio", "boliviano"]):
        return obtener_usdt()

    # Buenos días
    if any(p in t for p in ["buenos días", "buenos dias", "buen día", "buen dia", "bd", "me desperté", "me desperte", "desperté", "desperte"]):
        agenda = ver_eventos_hoy()
        tareas = ver_tasks()
        clima = obtener_clima()
        usdt = obtener_usdt()
        return (
            "☀️ *Buenos días!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{clima}\n\n"
            f"{usdt}\n\n"
            f"{agenda}\n\n"
            f"{tareas}"
        )

    # Buenas noches
    if any(p in t for p in ["buenas noches", "bn", "me voy a dormir", "a dormir", "good night"]):
        agenda_manana = get_agenda_manana()
        tareas = ver_tasks()
        usdt = obtener_usdt()
        luces = buenas_noches()
        return (
            "🌙 *Buenas noches!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{agenda_manana}\n\n"
            f"{tareas}\n\n"
            f"{usdt}\n\n"
            f"{luces}"
        )

    return "No entendí. Escribí *menu* para ver las opciones 🏠"