from handlers import casa, calendar, tasks, conversaciones
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import enviar_mensaje

# Números con acceso total (solo vos)
ADMIN = [
    "59167703883",  # Senka
]

# Números con acceso limitado (familia)
FAMILIA = [
     "59172157751",
     "59172153029",
             # agregá aquí cuando tengas los números
]

# Todos los autorizados
NUMEROS_AUTORIZADOS = ADMIN + FAMILIA

def menu_principal(es_admin=False):
    menu = (
        "🏠 *AsistentePersonal*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 *luces* — Control de luces\n"
        "🏠 *estado* — Estado luces\n"
        "🌙 *bn* — Buenas noches\n"
        "☀️ *bd* — Buenos días\n"
        "🌤️ *clima* — Clima Santa Cruz\n"
        "💲 *usdt* — Precio USDT\n"
    )
    if es_admin:
        menu += (
            "━━━━━━━━━━━━━━━━━━━\n"
            "📅 *agenda* — Ver eventos de hoy\n"
            "📅 *evento* — Crear evento\n"
            "✅ *tareas* — Ver Google Tasks\n"
            "✅ *tarea [texto]* — Agregar tarea\n"
            "⏱️ *timer [minutos]* — Temporizador\n"
        )
    menu += "━━━━━━━━━━━━━━━━━━━"
    return menu

def procesar(numero, texto):
    # Verificar acceso
    if numero not in NUMEROS_AUTORIZADOS:
        return "⛔ No tenés acceso a este asistente."

    es_admin = numero in ADMIN
    t = texto.lower().strip()

    # Conversación activa
    if conversaciones.activa(numero):
        if not es_admin:
            conversaciones.cancelar(numero)
            return "⛔ No tenés acceso a esa función."
        return conversaciones.continuar(numero, texto)

    # Menú
    if any(p in t for p in ["menu", "menú", "ayuda", "help", "inicio", "hola", "hey"]):
        return menu_principal(es_admin)

    # ── Solo admin ──────────────────────────────────────
    if not es_admin and any(p in t for p in ["evento", "agendar", "agenda", "tareas", "tarea", "timer", "temporizador"]):
        return "⛔ No tenés acceso a esa función."

    # Crear evento
    if any(p in t for p in ["evento", "agendar", "reunión", "reunion"]) and not any(p in t for p in ["ver", "mostrar", "hoy", "tengo"]):
        return conversaciones.iniciar_evento(numero)

    # Agenda hoy
    if any(p in t for p in ["agenda", "eventos", "qué tengo hoy", "que tengo hoy"]) and "mañana" not in t:
        return calendar.ver_hoy()

    # Tareas
    if any(p in t for p in ["tareas", "pendientes"]):
        return tasks.ver()
    if t.startswith("tarea ") or "nueva tarea" in t or "agregar tarea" in t:
        titulo = texto.split("tarea ", 1)[-1].strip()
        return tasks.agregar(titulo)

    # Timer
    if any(p in t for p in ["timer", "temporizador"]):
        nums = [s for s in t.split() if s.isdigit()]
        if nums:
            return iniciar_timer(numero, nums[0], enviar_mensaje)
        return "❌ Usá: *timer [minutos]*"

    # ── Todos los autorizados ───────────────────────────

    # Luces
    if any(p in t for p in ["luces", "luz", "focos", "nube", "espejo", "principal", "baño", "bano", "todo on", "todo off"]):
        return casa.procesar(t)

    # Estado luces
    if any(p in t for p in ["estado", "qué luces", "que luces"]):
        return casa.get_estado()

    # Clima
    if any(p in t for p in ["clima", "tiempo", "temperatura", "lluvia", "calor", "frio", "frío"]):
        return obtener_clima()

    # USDT
    if any(p in t for p in ["usdt", "dolar", "dólar", "precio", "cambio"]):
        return obtener_usdt()

    # Buenos días
    if any(p in t for p in ["buenos días", "buenos dias", "buen día", "buen dia", "bd", "desperté", "desperte"]):
        resumen = (
            "☀️ *Buenos días!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{obtener_clima()}\n\n"
            f"{obtener_usdt()}\n\n"
        )
        if es_admin:
            resumen += f"{calendar.ver_hoy()}\n\n{tasks.ver()}"
        return resumen

    # Buenas noches
    if any(p in t for p in ["buenas noches", "bn", "me voy a dormir", "a dormir"]):
        resumen = (
            "🌙 *Buenas noches!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
        )
        if es_admin:
            resumen += f"{calendar.ver_manana()}\n\n{tasks.ver()}\n\n{obtener_usdt()}\n\n"
        resumen += casa.buenas_noches()
        return resumen

    return "No entendí. Escribí *menu* para ver las opciones 🏠"