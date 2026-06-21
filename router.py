from handlers import casa, calendar, tasks, conversaciones
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import enviar_mensaje

def menu_principal():
    return (
        "🏠 *AsistentePersonal*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 *luces* — Control de luces\n"
        "📅 *agenda* — Ver eventos de hoy\n"
        "📅 *evento* — Crear evento\n"
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

def procesar(numero, texto):
    t = texto.lower().strip()

    # Conversación activa
    if conversaciones.activa(numero):
        return conversaciones.continuar(numero, texto)

    # Menú
    if any(p in t for p in ["menu", "menú", "ayuda", "help", "inicio", "hola", "hey"]):
        return menu_principal()

    # Crear evento
    if any(p in t for p in ["evento", "agendar", "reunión", "reunion"]) and not any(p in t for p in ["ver", "mostrar", "hoy", "tengo"]):
        return conversaciones.iniciar_evento(numero)

    # Luces
    if any(p in t for p in ["luces", "luz", "focos", "nube", "espejo", "principal", "baño", "bano", "todo on", "todo off"]):
        return casa.procesar(t)

    # Estado luces
    if any(p in t for p in ["estado", "qué luces", "que luces"]):
        return casa.get_estado()

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

    # Clima
    if any(p in t for p in ["clima", "tiempo", "temperatura", "lluvia", "calor", "frio", "frío"]):
        return obtener_clima()

    # USDT
    if any(p in t for p in ["usdt", "dolar", "dólar", "precio", "cambio"]):
        return obtener_usdt()

    # Buenos días
    if any(p in t for p in ["buenos días", "buenos dias", "buen día", "buen dia", "bd", "desperté", "desperte"]):
        return (
            "☀️ *Buenos días!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{obtener_clima()}\n\n"
            f"{obtener_usdt()}\n\n"
            f"{calendar.ver_hoy()}\n\n"
            f"{tasks.ver()}"
        )

    # Buenas noches
    if any(p in t for p in ["buenas noches", "bn", "me voy a dormir", "a dormir"]):
        return (
            "🌙 *Buenas noches!*\n"
            "━━━━━━━━━━━━━━━━━━━\n\n"
            f"{calendar.ver_manana()}\n\n"
            f"{tasks.ver()}\n\n"
            f"{obtener_usdt()}\n\n"
            f"{casa.buenas_noches()}"
        )

    return "No entendí. Escribí *menu* para ver las opciones 🏠"