from google_auth import get_tasks

def ver():
    try:
        svc = get_tasks()
        listas = svc.tasklists().list().execute().get('items', [])
        if not listas:
            return "📋 No tenés listas de tareas."
        tareas = svc.tasks().list(
            tasklist=listas[0]['id'], showCompleted=False
        ).execute().get('items', [])
        if not tareas:
            return "✅ No tenés tareas pendientes."
        resp = "📌 *Google Tasks:*\n━━━━━━━━━━━━━\n"
        for i, t in enumerate(tareas, 1):
            resp += f"{i}. {t['title']}\n"
        return resp
    except Exception as e:
        return f"❌ Error Tasks: {e}"

def agregar(titulo):
    try:
        svc = get_tasks()
        listas = svc.tasklists().list().execute().get('items', [])
        svc.tasks().insert(
            tasklist=listas[0]['id'], body={'title': titulo}
        ).execute()
        return f"✅ Tarea agregada: _{titulo}_"
    except Exception as e:
        return f"❌ Error: {e}"