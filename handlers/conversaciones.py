from datetime import datetime
import pytz

BOL = pytz.timezone("America/La_Paz")
_estado = {}

def activa(numero):
    return numero in _estado

def cancelar(numero):
    if numero in _estado:
        del _estado[numero]
    return "❌ Operación cancelada."

def iniciar_evento(numero, fn_fecha):
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
    if t in ["hoy", "today", "fecha_hoy"]:
        return hoy.strftime("%Y-%m-%d")
    elif t in ["mañana", "manana", "tomorrow", "fecha_manana"]:
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
    # IDs de la lista: hora_8, hora_12, etc.
    if t.startswith("hora_") and t != "hora_manual":
        h = t.replace("hora_", "")
        return f"{int(h):02d}:00"
    tarde = any(p in t for p in ["pm","tarde","noche"])
    manana = any(p in t for p in ["am","mañana"])
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

def continuar(numero, texto, fn_fecha, fn_horas, fn_mensaje):
    from handlers import calendar as cal_handler
    conv = _estado[numero]
    t = texto.lower().strip()

    if t in ["cancelar", "cancel", "salir"]:
        return cancelar(numero)

    if conv["flujo"] == "evento":

        if conv["paso"] == "titulo":
            _estado[numero]["datos"]["titulo"] = texto
            _estado[numero]["paso"] = "fecha"
            fn_fecha(numero)  # envía botones de fecha
            return None

        if conv["paso"] == "fecha":
            # Si eligió "Otra fecha", pedir texto
            if t == "fecha_manual":
                _estado[numero]["paso"] = "fecha_manual"
                return (
                    "✏️ Escribí la fecha:\n"
                    "• *25/06* (día/mes)\n"
                    "• *25/06/2026* (día/mes/año)"
                )
            fecha = parsear_fecha(texto)
            if not fecha:
                return "❌ No entendí. Escribí *hoy*, *mañana* o una fecha como *25/06*"
            _estado[numero]["datos"]["fecha"] = fecha
            _estado[numero]["paso"] = "hora"
            fn_horas(numero)  # envía lista de horas
            return None

        if conv["paso"] == "fecha_manual":
            fecha = parsear_fecha(texto)
            if not fecha:
                return "❌ No entendí la fecha. Probá: *25/06* o *25/06/2026*"
            _estado[numero]["datos"]["fecha"] = fecha
            _estado[numero]["paso"] = "hora"
            fn_horas(numero)  # envía lista de horas
            return None

        if conv["paso"] == "hora":
            # Si eligió "Otra hora", pedir texto
            if t == "hora_manual":
                _estado[numero]["paso"] = "hora_manual"
                return (
                    "✏️ Escribí la hora:\n"
                    "• *15:00* (24hs)\n"
                    "• *3 tarde* / *3pm*"
                )
            hora = parsear_hora(texto)
            if not hora:
                return "❌ No entendí la hora. Seleccioná de la lista o escribí *3 tarde*"
            datos = _estado[numero]["datos"]
            del _estado[numero]
            return cal_handler.crear(datos["titulo"], datos["fecha"], hora)

        if conv["paso"] == "hora_manual":
            hora = parsear_hora(texto)
            if not hora:
                return "❌ No entendí. Probá: *15:00* o *3 tarde*"
            datos = _estado[numero]["datos"]
            del _estado[numero]
            return cal_handler.crear(datos["titulo"], datos["fecha"], hora)

    return "❌ Error en la conversación. Escribí *cancelar*."