from handlers import casa, calendar, tasks, conversaciones, bnb
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import (enviar_mensaje, enviar_menu_principal, enviar_menu_casa,
                      enviar_menu_luces, enviar_menu_aire,
                      enviar_botones_fecha, enviar_lista_horas, enviar_botones,
                      enviar_imagen_qr)
import threading

ADMIN = ["59167703883"]
FAMILIA = ["59172157751", "59172153029", "59176970660"]
AMIGOS = ["59178560167","59178514955","59172639992","59177822509","59163541372","59171622488","59177807678"]
NUMEROS_AUTORIZADOS = ADMIN + FAMILIA + AMIGOS

def procesar(numero, texto, tipo="text", interactive_id=None):
    if numero not in NUMEROS_AUTORIZADOS:
        return "⛔ No tenés acceso a este asistente."

    es_admin   = numero in ADMIN
    es_familia = numero in FAMILIA
    es_amigo   = numero in AMIGOS
    t = texto.lower().strip() if texto else ""

    # ── Conversación activa ──────────────────────────────────────────────────
    if conversaciones.activa(numero):
        if not es_admin:
            conversaciones.cancelar(numero)
            return "⛔ No tenés acceso a esa función."
        entrada = interactive_id if interactive_id else texto
        return conversaciones.continuar(numero, entrada, enviar_botones_fecha, enviar_lista_horas, enviar_mensaje)

    # ── Interactivo ──────────────────────────────────────────────────────────
    if tipo == "interactive" and interactive_id:
        return _procesar_interactivo(numero, interactive_id, es_admin, es_familia, es_amigo)

    # ── Menú principal por texto ─────────────────────────────────────────────
    if any(p in t for p in ["menu", "menú", "ayuda", "help", "inicio", "hola", "hey"]):
        enviar_menu_principal(numero)
        return None

    # ── Bloqueos amigos ──────────────────────────────────────────────────────
    if es_amigo:
        if any(p in t for p in ["luces","luz","focos","nube","espejo","principal","baño","bano",
                                  "todo on","todo off","encend","apag","prend","bn","bd",
                                  "buenas noches","buenos dias","buenos días","aire","ac"]):
            return "👀 Modo demostración — solo podés ver clima, USDT y estado de luces."
        if any(p in t for p in ["evento","agendar","agenda","tareas","tarea","timer","temporizador"]):
            return "👀 Modo demostración — solo podés ver clima, USDT y estado de luces."

    # ── Bloqueos familia ─────────────────────────────────────────────────────
    if es_familia and any(p in t for p in ["evento","agendar","agenda","tareas","tarea","timer","temporizador"]):
        return "⛔ No tenés acceso a esa función."

    # ── Admin ────────────────────────────────────────────────────────────────
    if any(p in t for p in ["evento","agendar","reunión","reunion"]) and not any(p in t for p in ["ver","mostrar","hoy","tengo"]):
        return conversaciones.iniciar_evento(numero, enviar_botones_fecha)

    if any(p in t for p in ["agenda","eventos","qué tengo hoy","que tengo hoy"]) and "mañana" not in t:
        return calendar.ver_hoy()

    if any(p in t for p in ["tareas","pendientes"]):
        return tasks.ver()
    if t.startswith("tarea ") or "nueva tarea" in t or "agregar tarea" in t:
        titulo = texto.split("tarea ", 1)[-1].strip()
        return tasks.agregar(titulo)

    if any(p in t for p in ["timer","temporizador"]):
        nums = [s for s in t.split() if s.isdigit()]
        if nums:
            return iniciar_timer(numero, nums[0], enviar_mensaje)
        return "❌ Usá: *timer [minutos]*"

    # ── Cobro QR BNB ─────────────────────────────────────────────────────────
    if any(p in t for p in ["cobrar","cobro","qr"]):
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        monto, gloss, error = bnb.procesar_cobro(texto)
        if error:
            return error
        threading.Thread(
            target=bnb.generar_qr,
            args=(numero, monto, gloss, enviar_imagen_qr, enviar_mensaje),
            daemon=True
        ).start()
        return "⏳ Generando QR de cobro..."

    # ── Casa ──────────────────────────────────────────────────────────────────
    if t == "casa":
        enviar_menu_casa(numero)
        return None

    # ── Aire ─────────────────────────────────────────────────────────────────
    if any(p in t for p in ["aire","ac","acondicionado"]):
        if any(p in t for p in ["on","encend","prend"]):
            return casa.aire_on()
        elif any(p in t for p in ["off","apag"]):
            return casa.aire_off()
        else:
            enviar_menu_aire(numero)
            return None

    # ── Luces ─────────────────────────────────────────────────────────────────
    if any(p in t for p in ["luces","luz","focos","nube","espejo","principal","baño","bano","todo on","todo off"]):
        enviar_menu_luces(numero)
        return None

    if any(p in t for p in ["estado","qué luces","que luces"]):
        return casa.get_estado()

    # ── Info ──────────────────────────────────────────────────────────────────
    if any(p in t for p in ["clima","tiempo","temperatura","lluvia","calor","frio","frío"]):
        return obtener_clima()

    if any(p in t for p in ["usdt","dolar","dólar","precio","cambio"]):
        return obtener_usdt()

    # ── Rutinas ───────────────────────────────────────────────────────────────
    if any(p in t for p in ["buenos días","buenos dias","buen día","buen dia","bd","desperté","desperte"]):
        resumen = f"☀️ *Buenos días!*\n━━━━━━━━━━━━━━━━━━━\n\n{obtener_clima()}\n\n{obtener_usdt()}\n\n"
        if es_admin:
            resumen += f"{calendar.ver_hoy()}\n\n{tasks.ver()}"
        return resumen

    if any(p in t for p in ["buenas noches","bn","me voy a dormir","a dormir"]):
        resumen = "🌙 *Buenas noches!*\n━━━━━━━━━━━━━━━━━━━\n\n"
        if es_admin:
            resumen += f"{calendar.ver_manana()}\n\n{tasks.ver()}\n\n{obtener_usdt()}\n\n"
        resumen += casa.buenas_noches()
        return resumen

    return "No entendí. Escribí *menu* para ver las opciones 🏠"


def _procesar_interactivo(numero, iid, es_admin, es_familia, es_amigo):

    if iid == "volver_principal":
        enviar_menu_principal(numero)
        return None

    if iid == "volver_casa":
        enviar_menu_casa(numero)
        return None

    if iid == "menu_casa":
        if es_amigo:
            return "👀 Modo demostración — no podés controlar la casa."
        enviar_menu_casa(numero)
        return None

    if iid == "menu_luces":
        if es_amigo:
            return "👀 Modo demostración — no podés controlar las luces."
        enviar_menu_luces(numero)
        return None

    if iid == "menu_aire":
        if es_amigo:
            return "👀 Modo demostración — no podés controlar el aire."
        enviar_menu_aire(numero)
        return None

    if iid == "menu_agenda":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return calendar.ver_hoy()

    if iid == "menu_tareas":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return tasks.ver()

    if iid == "menu_clima":
        return obtener_clima()

    if iid == "menu_usdt":
        return obtener_usdt()

    if iid == "luz_on_all":
        resp = casa.todo_on()
        enviar_menu_luces(numero)
        return resp

    if iid == "luz_off_all":
        resp = casa.todo_off()
        enviar_menu_luces(numero)
        return resp

    if iid.startswith("luz_on_"):
        luz_id = iid.replace("luz_on_", "")
        resp = casa.encender(luz_id)
        enviar_menu_luces(numero)
        return resp

    if iid.startswith("luz_off_"):
        luz_id = iid.replace("luz_off_", "")
        resp = casa.apagar(luz_id)
        enviar_menu_luces(numero)
        return resp

    if iid == "aire_on":
        resp = casa.aire_on()
        enviar_menu_aire(numero)
        return resp

    if iid == "aire_off":
        resp = casa.aire_off()
        enviar_menu_aire(numero)
        return resp

    return None