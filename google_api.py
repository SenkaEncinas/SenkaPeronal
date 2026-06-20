from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

BOL = pytz.timezone("America/La_Paz")

def get_services():
    creds = Credentials.from_authorized_user_file('google_token.json')
    calendar = build('calendar', 'v3', credentials=creds)
    tasks = build('tasks', 'v1', credentials=creds)
    return calendar, tasks

def ver_eventos_hoy():
    try:
        calendar, _ = get_services()
        ahora = datetime.now(BOL).isoformat()
        fin = (datetime.now(BOL) + timedelta(days=1)).isoformat()
        eventos = calendar.events().list(
            calendarId='primary',
            timeMin=ahora, timeMax=fin,
            singleEvents=True, orderBy='startTime'
        ).execute().get('items', [])
        if not eventos:
            return "📅 No tenés eventos hoy."
        resp = "📅 *Eventos de hoy:*\n━━━━━━━━━━━━━\n"
        for e in eventos:
            inicio = e['start'].get('dateTime', e['start'].get('date'))
            hora = datetime.fromisoformat(inicio).strftime('%H:%M') if 'T' in inicio else "Todo el día"
            resp += f"🕐 {hora} — {e['summary']}\n"
        return resp
    except Exception as e:
        return f"❌ Error Calendar: {e}"

def crear_evento(titulo, fecha_str, hora_str):
    try:
        calendar, _ = get_services()
        hoy = datetime.now(BOL)
        if fecha_str == "hoy":
            fecha = hoy.strftime("%Y-%m-%d")
        elif fecha_str in ["mañana", "manana"]:
            fecha = (hoy + timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            fecha = fecha_str
        inicio = BOL.localize(datetime.strptime(f"{fecha} {hora_str}", "%Y-%m-%d %H:%M"))
        fin = inicio + timedelta(hours=1)
        evento = {
            'summary': titulo,
            'start': {'dateTime': inicio.isoformat(), 'timeZone': 'America/La_Paz'},
            'end': {'dateTime': fin.isoformat(), 'timeZone': 'America/La_Paz'},
        }
        calendar.events().insert(calendarId='primary', body=evento).execute()
        return f"📅 Evento: *{titulo}*\n🕐 {inicio.strftime('%d/%m/%Y %H:%M')}"
    except Exception as e:
        return f"❌ Error: {e}"

def ver_tasks():
    try:
        _, tasks_service = get_services()
        listas = tasks_service.tasklists().list().execute().get('items', [])
        if not listas:
            return "📋 No tenés listas de tareas."
        tareas = tasks_service.tasks().list(
            tasklist=listas[0]['id'], showCompleted=False
        ).execute().get('items', [])
        if not tareas:
            return "✅ No tenés tareas en Google Tasks."
        resp = "📌 *Google Tasks:*\n━━━━━━━━━━━━━\n"
        for i, t in enumerate(tareas, 1):
            resp += f"{i}. {t['title']}\n"
        return resp
    except Exception as e:
        return f"❌ Error Tasks: {e}"

def agregar_task(titulo):
    try:
        _, tasks_service = get_services()
        listas = tasks_service.tasklists().list().execute().get('items', [])
        tasks_service.tasks().insert(
            tasklist=listas[0]['id'], body={'title': titulo}
        ).execute()
        return f"✅ Google Task: _{titulo}_"
    except Exception as e:
        return f"❌ Error: {e}"