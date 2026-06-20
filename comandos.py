from casa import LUCES, encender, apagar, todo_on, todo_off, get_estado, menu_luces, buenas_noches, buenos_dias
from firebase_db import guardar_nota, ver_notas, agregar_tarea, ver_tareas, marcar_hecho, registrar_gasto, ver_gastos, ver_contacto
from google_api import ver_eventos_hoy, crear_evento, ver_tasks, agregar_task
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import enviar_mensaje

def menu_principal():
    return (
        "🏠 *AsistentePersonal — Menú*\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "💡 *luces* — Control de luces\n"
        "📅 *agenda* — Ver eventos de hoy\n"
        "📅 *evento [titulo] [hoy/mañana] [HH:MM]*\n"
        "📌 *gtareas* — Google Tasks\n"
        "✅ *gtarea [texto]* — Agregar Google Task\n"
        "📝 *nota [texto]* — Guardar nota\n"
        "📋 *notas* — Ver notas\n"
        "✅ *tarea [texto]* — Agregar tarea\n"
        "📌 *tareas* — Ver tareas\n"
        "✔️ *hecho [número]* — Marcar lista\n"
        "💰 *gasto [monto] [desc]* — Registrar\n"
        "💵 *gastos* — Ver gastos del mes\n"
        "👤 *contacto [nombre]*\n"
        "⏱️ *timer [minutos]*\n"
        "🌤️ *clima*\n"
        "💲 *usdt*\n"
        "🏠 *estado* — Estado luces\n"
        "🌙 *buenas noches*\n"
        "☀️ *buenos días*\n"
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

    if t == "gtareas":
        return ver_tasks()
    if t.startswith("gtarea "):
        return agregar_task(texto[7:])

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
            return iniciar_timer(numero, t.split()[1], enviar_mensaje)
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