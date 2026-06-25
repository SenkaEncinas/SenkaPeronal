from google_auth import get_calendar
from datetime import datetime, timedelta
import pytz

BOL = pytz.timezone("America/La_Paz")

def ver_hoy():
    try:
        cal = get_calendar()
        hoy = datetime.now(BOL)
        inicio = hoy.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        fin = hoy.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        eventos = cal.events().list(
            calendarId='primary',
            timeMin=inicio, timeMax=fin,
            singleEvents=True, orderBy='startTime'
        ).execute().get('items', [])
        if not eventos:
            return "📅 No tenés eventos hoy."
        resp = "📅 *Eventos de hoy:*\n━━━━━━━━━━━━━\n"
        for e in eventos:
            inicio_e = e['start'].get('dateTime', e['start'].get('date'))
            hora = datetime.fromisoformat(inicio_e).strftime('%H:%M') if 'T' in inicio_e else "Todo el día"
            resp += f"🕐 {hora} — {e['summary']}\n"
        return resp
    except Exception as e:
        return f"❌ Error Calendar: {e}"

def ver_manana():
    try:
        cal = get_calendar()
        manana = datetime.now(BOL) + timedelta(days=1)
        inicio = manana.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        fin = manana.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        eventos = cal.events().list(
            calendarId='primary',
            timeMin=inicio, timeMax=fin,
            singleEvents=True, orderBy='startTime'
        ).execute().get('items', [])
        if not eventos:
            return "📅 No tenés eventos mañana."
        resp = "📅 *Eventos de mañana:*\n━━━━━━━━━━━━━\n"
        for e in eventos:
            inicio_e = e['start'].get('dateTime', e['start'].get('date'))
            hora = datetime.fromisoformat(inicio_e).strftime('%H:%M') if 'T' in inicio_e else "Todo el día"
            resp += f"🕐 {hora} — {e['summary']}\n"
        return resp
    except Exception as e:
        return f"❌ Error: {e}"

def crear(titulo, fecha_str, hora_str):
    try:
        cal = get_calendar()
        hoy = datetime.now(BOL)
        if fecha_str in ["hoy", "today"]:
            fecha = hoy.strftime("%Y-%m-%d")
        elif fecha_str in ["mañana", "manana", "tomorrow"]:
            fecha = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "/" in fecha_str:
            partes = fecha_str.split("/")
            if len(partes) == 2:
                fecha = f"{hoy.year}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
            else:
                fecha = f"{partes[2]}-{partes[1].zfill(2)}-{partes[0].zfill(2)}"
        else:
            fecha = fecha_str
        inicio = BOL.localize(datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M"))
        fin = inicio + timedelta(hours=1)
        evento = {
            'summary': titulo,
            'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/La_Paz'},
            'end': {'dateTime': fin.isoformat(), 'timeZone': 'America/La_Paz'},
        }
        cal.events().insert(calendarId='primary', body=evento).execute()
        return f"📅 Evento creado: *{titulo}*\n🕐 {inicio.strftime('%d/%m/%Y %H:%M')}"
    except Exception as e:
        return f"❌ Error: {e}"