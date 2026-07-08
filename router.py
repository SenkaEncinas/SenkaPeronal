from handlers import casa, calendar, tasks, conversaciones, bnb
from utils import obtener_clima, obtener_usdt, iniciar_timer
from whatsapp import (enviar_mensaje, enviar_menu_principal, enviar_menu_casa,
                      enviar_menu_luces, enviar_menu_aire, enviar_menu_finanzas,
                      enviar_menu_bnb_consultas, enviar_botones_fecha,
                      enviar_lista_horas, enviar_botones, enviar_imagen_qr)
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

    if conversaciones.activa(numero):
        if not es_admin:
            conversaciones.cancelar(numero)
            return "⛔ No tenés acceso a esa función."
        entrada = interactive_id if interactive_id else texto
        return conversaciones.continuar(numero, entrada, enviar_botones_fecha, enviar_lista_horas, enviar_mensaje)

    if tipo == "interactive" and interactive_id:
        return _procesar_interactivo(numero, interactive_id, es_admin, es_familia, es_amigo)

    if any(p in t for p in ["menu", "menú", "ayuda", "help", "inicio", "hola", "hey"]):
        enviar_menu_principal(numero)
        return None

    if es_amigo:
        if any(p in t for p in ["luces","luz","focos","nube","espejo","principal","baño","bano",
                                  "todo on","todo off","encend","apag","prend","bn","bd",
                                  "buenas noches","buenos dias","buenos días","aire","ac"]):
            return "👀 Modo demostración — solo podés ver clima, USDT y estado de luces."
        if any(p in t for p in ["evento","agendar","agenda","tareas","tarea","timer","temporizador",
                                  "cobrar","pagar","saldo","movimientos"]):
            return "👀 Modo demostración — solo podés ver clima, USDT y estado de luces."

    if es_familia and any(p in t for p in ["evento","agendar","agenda","tareas","tarea","timer","temporizador",
                                            "cobrar","pagar","saldo","movimientos"]):
        return "⛔ No tenés acceso a esa función."

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

    # ── BNB ───────────────────────────────────────────────────────────────────
    if any(p in t for p in ["cobrar","cobro"]):
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

    if t.startswith("pagar "):
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        cuenta, monto, referencia, error = bnb.procesar_pago(texto)
        if error:
            return error
        return bnb.pagar_qr(cuenta, monto, referencia)

    if t.startswith("estado qr "):
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        qr_id = t.replace("estado qr ", "").strip()
        return bnb.estado_qr(qr_id)

    if t == "qrs hoy":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return bnb.qrs_hoy()

    if t.startswith("cancelar qr "):
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        qr_id = t.replace("cancelar qr ", "").strip()
        return bnb.cancelar_qr(qr_id)

    if t in ["saldo", "movimientos"]:
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return bnb.consultar_saldo()

    if any(p in t for p in ["finanzas","bnb"]):
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        enviar_menu_finanzas(numero)
        return None

    # ── Casa ──────────────────────────────────────────────────────────────────
    if t == "casa":
        enviar_menu_casa(numero)
        return None

    if any(p in t for p in ["aire","ac","acondicionado"]):
        if any(p in t for p in ["on","encend","prend"]):
            return casa.aire_on()
        elif any(p in t for p in ["off","apag"]):
            return casa.aire_off()
        else:
            enviar_menu_aire(numero)
            return None

    if any(p in t for p in ["luces","luz","focos","nube","espejo","principal","baño","bano","todo on","todo off"]):
        enviar_menu_luces(numero)
        return None

    if any(p in t for p in ["estado","qué luces","que luces"]):
        return casa.get_estado()

    if any(p in t for p in ["clima","tiempo","temperatura","lluvia","calor","frio","frío"]):
        return obtener_clima()

    if any(p in t for p in ["usdt","dolar","dólar","precio","cambio"]):
        return obtener_usdt()

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

    if iid == "volver_finanzas":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        enviar_menu_finanzas(numero)
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

    if iid == "menu_finanzas":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        enviar_menu_finanzas(numero)
        return None

    if iid == "bnb_consultas":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        enviar_menu_bnb_consultas(numero)
        return None

    if iid == "bnb_cobrar":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return (
            "📥 *Generar QR de cobro*\n"
            "━━━━━━━━━━━━━━━\n"
            "Escribí: *cobrar [monto] [descripción]*\n\n"
            "Ejemplo:\n*cobrar 50 Almuerzo*"
        )

    if iid == "bnb_saldo":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return bnb.consultar_saldo()

    if iid == "bnb_qrs_hoy":
        if not es_admin:
            return "⛔ No tenés acceso a esa función."
        return bnb.qrs_hoy()

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