from datetime import datetime
import pytz

BOL = pytz.timezone("America/La_Paz")

# Estado de conversaciones activas
_estado = {}

def activa(numero):
    return numero in _estado

def cancelar(numero):
    if numero in _estado:
        del _estado[numero]
    return "❌ Operación cancelada."

def iniciar_evento(numero):
    _estado[numero] = {"flujo": "evento", "paso": "titulo", "datos": {}}
    return (
        "📅 *Crear evento*\n"
        "━━━━━━━━━━━━━━━\n"
        "¿Cómo se llama el evento?\n\n"
        "Ej: *Reunión con el doctor*\n"
        "_(Escribí *cancelar* para salir)_"
    )

def parsear_fecha(texto):
    t = texto.lower().strip()
    hoy = datetime.now(BOL)
    if t in ["hoy", "today"]:
        return hoy.strftime("%Y-%m-%d")
    elif t in ["mañana", "manana", "tomorrow"]:
        from datetime import timedelta
        return (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "/" in t:
        partes = t.split("/")
        try:
            if len(partes) == 2:
                return f"{hoy.year}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
            else:
                return f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
        except:
            return None
    return None

def parsear_hora(texto):
    t = texto.lower().strip()
    tarde = any(p in t for p in ["pm", "tarde", "noche"])
    manana = any(p in t for p in ["am", "mañana"])
    t = t.replace("pm","").replace("am","").replace("tarde","").replace("mañana","").replace("noche","").replace(":","").replace("hs","").replace("hrs","").strip()
    try:
        if len(t) <= 2:
            hora = int(t)
            if tarde and hora != 12: hora += 12
            if manana and hora == 12: hora = 0
            return f"{hora:02d}:00"
        elif len(t) == 3:
            return f"0{t[0]}:{t[1:]}"
        elif len(t) == 4:
            return f"{t[:2]}:{t[2:]}"
    except:
        return None
    return None

def continuar(numero, texto):
    from handlers import calendar as cal_handler
    conv = _estado[numero]
    t = texto.lower().strip()

    if t in ["cancelar", "cancel", "salir"]:
        return cancelar(numero)

    if conv["flujo"] == "evento":
        if conv["paso"] == "titulo":
            _estado[numero]["datos"]["titulo"] = texto
            _estado[numero]["paso"] = "fecha"
            return (
                "📅 *¿Para qué día?*\n"
                "━━━━━━━━━━━━━━━\n"
                "• *hoy*\n"
                "• *mañana*\n"
                "• *25/06* (día/mes)\n"
                "• *25/06/2026* (día/mes/año)"
            )

        if conv["paso"] == "fecha":
            fecha = parsear_fecha(texto)
            if not fecha:
                return (
                    "❌ No entendí la fecha. Probá:\n"
                    "• *hoy* / *mañana*\n"
                    "• *25/06* / *25/06/2026*"
                )
            _estado[numero]["datos"]["fecha"] = fecha
            _estado[numero]["paso"] = "hora"
            return (
                "🕐 *¿A qué hora?*\n"
                "━━━━━━━━━━━━━━━\n"
                "• *15:00* (24hs)\n"
                "• *3 tarde* / *3pm*\n"
                "• *10 mañana* / *10am*"
            )

        if conv["paso"] == "hora":
            hora = parsear_hora(texto)
            if not hora:
                return (
                    "❌ No entendí la hora. Probá:\n"
                    "• *15:00*\n"
                    "• *3 tarde* / *3pm*"
                )
            datos = _estado[numero]["datos"]
            del _estado[numero]
            return cal_handler.crear(datos["titulo"], datos["fecha"], hora)

    return "❌ Error en la conversación. Escribí *cancelar*."