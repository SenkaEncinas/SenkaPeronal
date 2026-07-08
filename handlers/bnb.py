import requests
import threading
import time
import os
from datetime import datetime, timedelta

BNB_ACCOUNT_ID = os.environ.get("BNB_ACCOUNT_ID")
BNB_AUTH_ID = os.environ.get("BNB_AUTH_ID")
BNB_USER_KEY = os.environ.get("BNB_USER_KEY")
BNB_ACCOUNT_NUMBER = os.environ.get("BNB_ACCOUNT_NUMBER", "2505116979")

TOKEN_URL = "https://clientauthenticationapiv2.azurewebsites.net/api/v1/auth/token"
QR_GENERAR_URL = "https://qrsimpleapiv2.azurewebsites.net/api/v1/main/getQRWithImageAsync"
QR_STATUS_URL = "https://qrsimpleapiv2.azurewebsites.net/api/v1/main/getQRStatusAsync"
QR_LISTA_URL = "https://qrsimpleapiv2.azurewebsites.net/api/v1/main/getQRbyGenerationDateAsync"
QR_CANCELAR_URL = "https://qrsimpleapiv2.azurewebsites.net/api/v1/main/CancelQRByIdAsync"
SALDO_URL = "http://bnbapideveloperv1.azurewebsites.net/Enterprise/BankStatement"
TRANSFERIR_URL = "http://bnbapideveloperv1.azurewebsites.net/Enterprise/TransferQR"

qrs_activos = {}

def obtener_token():
    try:
        r = requests.post(TOKEN_URL, json={
            "accountid": BNB_ACCOUNT_ID,
            "authorizationid": BNB_AUTH_ID
        }, headers={"Content-Type": "application/json"}, timeout=10)
        data = r.json()
        if data.get("success"):
            return data["message"]
        return None
    except Exception as e:
        print(f"Error token BNB: {e}")
        return None

def _headers(token):
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "cache-control": "no-cache"
    }

# ─── Generar QR de cobro ──────────────────────────────────────────────────────

def generar_qr(numero, monto, gloss, fn_enviar_imagen, fn_enviar_mensaje):
    try:
        token = obtener_token()
        if not token:
            fn_enviar_mensaje(numero, "❌ Error al conectar con el BNB")
            return

        expiracion = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        body = {
            "currency": "BOB",
            "gloss": gloss,
            "amount": float(monto),
            "singleUse": True,
            "expirationDate": expiracion,
            "additionalData": f"AsistentePersonal - {gloss}",
            "destinationAccountId": "1"
        }
        r = requests.post(QR_GENERAR_URL, json=body, headers=_headers(token), timeout=15)
        data = r.json()

        if not data.get("success"):
            fn_enviar_mensaje(numero, f"❌ Error BNB: {data.get('message')}")
            return

        qr_id = data.get("id") or data.get("qrCode")
        qr_bytes = data.get("qr")

        qrs_activos[qr_id] = {
            "numero": numero,
            "monto": monto,
            "gloss": gloss
        }

        fn_enviar_imagen(
            numero,
            qr_bytes,
            caption=f"💳 *{gloss}*\n💵 Monto: *{monto} Bs*\n⏳ Válido por 24 horas\n🆔 ID: {qr_id}"
        )

        threading.Thread(
            target=_verificar_loop,
            args=(qr_id, fn_enviar_mensaje),
            daemon=True
        ).start()

    except Exception as e:
        fn_enviar_mensaje(numero, f"❌ Error generando QR: {e}")

# ─── Verificar pago en loop ───────────────────────────────────────────────────

def _verificar_loop(qr_id, fn_enviar_mensaje):
    token = obtener_token()
    if not token:
        return

    intentos = 0
    max_intentos = 120  # 1 hora máximo

    while intentos < max_intentos:
        time.sleep(30)
        try:
            r = requests.post(
                QR_STATUS_URL,
                json={"qrId": qr_id},
                headers=_headers(token),
                timeout=10
            )
            data = r.json()
            status = data.get("statusId")
            info = qrs_activos.get(qr_id)

            if not info:
                break

            if status == 2:
                voucher = data.get("voucherId", "N/A")
                fn_enviar_mensaje(
                    info["numero"],
                    f"✅ *{info['monto']} Bs de {info['gloss']} ya fueron pagados*\n🧾 Voucher: {voucher}"
                )
                del qrs_activos[qr_id]
                break

            elif status == 3:
                fn_enviar_mensaje(
                    info["numero"],
                    f"⌛ El QR de *{info['gloss']}* expiró sin ser pagado."
                )
                del qrs_activos[qr_id]
                break

            elif status == 4:
                fn_enviar_mensaje(
                    info["numero"],
                    f"❌ Error en el QR de *{info['gloss']}*."
                )
                del qrs_activos[qr_id]
                break

        except:
            pass

        intentos += 1

# ─── Estado de un QR manual ──────────────────────────────────────────────────

def estado_qr(qr_id):
    try:
        token = obtener_token()
        if not token:
            return "❌ Error al conectar con el BNB"

        r = requests.post(
            QR_STATUS_URL,
            json={"qrId": int(qr_id)},
            headers=_headers(token),
            timeout=10
        )
        data = r.json()
        if not data.get("success"):
            return f"❌ Error: {data.get('message')}"

        status = data.get("statusId")
        expiracion = data.get("expirationDate", "")[:10]
        voucher = data.get("voucherId")

        estados = {1: "⏳ Pendiente", 2: "✅ Pagado", 3: "⌛ Expirado", 4: "❌ Con error"}
        estado_txt = estados.get(status, "❓ Desconocido")

        resp = f"🆔 QR #{qr_id}\n{estado_txt}\n📅 Vence: {expiracion}"
        if voucher:
            resp += f"\n🧾 Voucher: {voucher}"
        return resp
    except Exception as e:
        return f"❌ Error: {e}"

# ─── QRs del día ─────────────────────────────────────────────────────────────

def qrs_hoy():
    try:
        token = obtener_token()
        if not token:
            return "❌ Error al conectar con el BNB"

        hoy = datetime.now().strftime("%Y-%m-%d")
        r = requests.post(
            QR_LISTA_URL,
            json={"generationDate": hoy},
            headers=_headers(token),
            timeout=10
        )
        data = r.json()
        if not data.get("success"):
            return f"❌ Error: {data.get('message')}"

        lista = data.get("dTOqrDetails", [])
        if not lista:
            return "📋 No hay QRs generados hoy."

        estados = {1: "⏳", 2: "✅", 3: "⌛", 4: "❌"}
        resp = "📋 *QRs de hoy:*\n━━━━━━━━━━━━━\n"
        for q in lista:
            estado = estados.get(q.get("statusId"), "❓")
            resp += f"{estado} #{q['id']} — {q['amount']} Bs — {q['gloss']}\n"
        return resp
    except Exception as e:
        return f"❌ Error: {e}"

# ─── Cancelar QR ─────────────────────────────────────────────────────────────

def cancelar_qr(qr_id):
    try:
        token = obtener_token()
        if not token:
            return "❌ Error al conectar con el BNB"

        r = requests.post(
            QR_CANCELAR_URL,
            json={"qrId": int(qr_id)},
            headers=_headers(token),
            timeout=10
        )
        data = r.json()
        if data.get("success"):
            return f"✅ QR #{qr_id} cancelado correctamente"
        return f"❌ Error: {data.get('message')}"
    except Exception as e:
        return f"❌ Error: {e}"

# ─── Consulta de saldo ────────────────────────────────────────────────────────

def consultar_saldo():
    try:
        r = requests.post(
            SALDO_URL,
            json={
                "userKey": BNB_USER_KEY,
                "accountNumber": BNB_ACCOUNT_NUMBER
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        data = r.json()
        if data.get("success"):
            movimientos = data.get("message", [])
            if not movimientos:
                return "💰 Sin movimientos recientes."
            resp = "💰 *Últimos movimientos:*\n━━━━━━━━━━━━━\n"
            for m in movimientos[:5]:
                resp += f"• {m.get('date','')[:10]} — {m.get('amount','')} Bs — {m.get('description','')}\n"
            return resp
        return f"❌ Error: {data.get('message')}"
    except Exception as e:
        return f"❌ Error: {e}"

# ─── Pagar QR (transferencia) ─────────────────────────────────────────────────

def pagar_qr(cuenta_destino, monto, referencia):
    try:
        r = requests.post(
            TRANSFERIR_URL,
            json={
                "userKey": BNB_USER_KEY,
                "sourceAccountNumber": BNB_ACCOUNT_NUMBER,
                "destinationAccountNumber": cuenta_destino,
                "currency": "2003",
                "ammount": str(monto),
                "reference": referencia,
                "onlyUse": False
            },
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        data = r.json()
        if data.get("success"):
            return f"✅ Pago enviado\n💵 {monto} Bs → cuenta {cuenta_destino}\n📝 Ref: {referencia}"
        return f"❌ Error: {data.get('message')}"
    except Exception as e:
        return f"❌ Error: {e}"

# ─── Parser de comandos ───────────────────────────────────────────────────────

def procesar_cobro(texto):
    partes = texto.strip().split(" ", 2)
    if len(partes) < 3:
        return None, None, "❌ Usá: *cobrar [monto] [descripción]*\nEj: *cobrar 10 Pago Wally*"
    try:
        monto = float(partes[1])
        gloss = partes[2]
        return monto, gloss, None
    except:
        return None, None, "❌ El monto debe ser un número. Ej: *cobrar 10.5 Alquiler*"

def procesar_pago(texto):
    partes = texto.strip().split(" ", 3)
    if len(partes) < 4:
        return None, None, None, "❌ Usá: *pagar [cuenta] [monto] [referencia]*\nEj: *pagar 1234567890 50 Alquiler*"
    try:
        cuenta = partes[1]
        monto = float(partes[2])
        referencia = partes[3]
        return cuenta, monto, referencia, None
    except:
        return None, None, None, "❌ Formato incorrecto. Ej: *pagar 1234567890 50 Alquiler*"