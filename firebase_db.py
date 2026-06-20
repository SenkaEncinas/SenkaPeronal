import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import pytz

BOL = pytz.timezone("America/La_Paz")

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def guardar_nota(numero, texto):
    db.collection("notas").add({
        "numero": numero, "texto": texto,
        "fecha": datetime.now(BOL).isoformat()
    })
    return f"📝 Nota guardada: _{texto}_"

def ver_notas(numero):
    docs = db.collection("notas").where("numero", "==", numero).limit(10).stream()
    notas = list(docs)
    if not notas:
        return "📝 No tenés notas guardadas."
    resp = "📋 *Tus notas:*\n━━━━━━━━━━━━━\n"
    for i, doc in enumerate(notas, 1):
        resp += f"{i}. {doc.to_dict()['texto']}\n"
    return resp

def agregar_tarea(numero, texto):
    db.collection("tareas").add({
        "numero": numero, "texto": texto,
        "hecho": False, "fecha": datetime.now(BOL).isoformat()
    })
    return f"✅ Tarea agregada: _{texto}_"

def ver_tareas(numero):
    docs = db.collection("tareas").where("numero", "==", numero).where("hecho", "==", False).limit(10).stream()
    tareas = list(docs)
    if not tareas:
        return "✅ No tenés tareas pendientes."
    resp = "📌 *Tareas pendientes:*\n━━━━━━━━━━━━━\n"
    for i, doc in enumerate(tareas, 1):
        resp += f"{i}. {doc.to_dict()['texto']}\n"
    return resp

def marcar_hecho(numero, indice):
    docs = list(db.collection("tareas").where("numero", "==", numero).where("hecho", "==", False).limit(10).stream())
    if indice < 1 or indice > len(docs):
        return "❌ Número de tarea inválido."
    doc = docs[indice - 1]
    doc.reference.update({"hecho": True})
    return f"✔️ Completada: _{doc.to_dict()['texto']}_"

def registrar_gasto(numero, monto, descripcion):
    db.collection("gastos").add({
        "numero": numero, "monto": float(monto),
        "descripcion": descripcion,
        "fecha": datetime.now(BOL).isoformat(),
        "mes": datetime.now(BOL).strftime("%Y-%m")
    })
    return f"💰 Gasto: *{monto} Bs* — {descripcion}"

def ver_gastos(numero):
    mes = datetime.now(BOL).strftime("%Y-%m")
    docs = db.collection("gastos").where("numero", "==", numero).where("mes", "==", mes).limit(50).stream()
    gastos = list(docs)
    if not gastos:
        return "💵 No tenés gastos este mes."
    total = 0
    resp = f"💰 *Gastos de {mes}:*\n━━━━━━━━━━━━━\n"
    for doc in gastos:
        d = doc.to_dict()
        resp += f"• {d['descripcion']}: *{d['monto']} Bs*\n"
        total += d['monto']
    resp += f"━━━━━━━━━━━━━\n*Total: {total} Bs*"
    return resp

def ver_contacto(nombre):
    docs = db.collection("contactos").where("nombre", "==", nombre.lower()).limit(1).stream()
    contactos = list(docs)
    if not contactos:
        return f"👤 No encontré _{nombre}_."
    d = contactos[0].to_dict()
    resp = f"👤 *{d.get('nombre', '').title()}*\n━━━━━━━━━━━━━\n"
    for k, v in d.items():
        if k != "nombre":
            resp += f"• {k}: {v}\n"
    return resp