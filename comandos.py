from casa import LUCES, encender, apagar, todo_on, todo_off, get_estado, menu_luces, buenas_noches, buenos_dias
from google_api import ver_eventos_hoy, crear_evento, ver_tasks, agregar_task
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import enviar_mensaje

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

def procesar_mensaje(numero, texto):
    t = texto.lower().strip()

    if t in ["menu", "menú", "hola", "inicio", "ayuda", "help"]:
        return menu_principal()

    if t in ["luces", "luz"]:
        return menu_luces()

    if t == "todo on":
        return todo_on()
    if t == "todo off":
        return todo_off()

    for luz_id in LUCES:
        if t.startswith(luz_id + " "):
            if any(p in t for p in ["on", "encend", "prend"]):
                return encender(luz_id)
            elif any(p in t for p in ["off", "apag"]):
                return apagar(luz_id)

    if t == "estado":
        return get_estado()

    if t in ["agenda", "hoy"]:
        return ver_eventos_hoy()

    if t.startswith("evento "):
        try:
            partes = texto.split(" ", 3)
            return crear_evento(partes[1], partes[2], partes[3])
        except:
            return "❌ Usá: *evento [titulo] [hoy/mañana] [HH:MM]*"

    if t == "tareas":
        return ver_tasks()
    if t.startswith("tarea "):
        return agregar_task(texto[6:])

    if t.startswith("timer "):
        try:
            return iniciar_timer(numero, t.split()[1], enviar_mensaje)
        except:
            return "❌ Usá: *timer [minutos]*"

    if t == "clima":
        return obtener_clima()

    if t in ["usdt", "dolar", "dólar"]:
        return obtener_usdt()

    if t in ["bn", "buenas noches"]:
        return buenas_noches()
    if t in ["bd", "buenos días", "buenos dias"]:
        return buenos_dias()

    return "No entendí. Escribí *menu* para ver las opciones 🏠"