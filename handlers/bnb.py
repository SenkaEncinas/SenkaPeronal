import requests
import threading
import time
from datetime import datetime, timedelta

import os

BNB_ACCOUNT_ID = os.environ.get("BNB_ACCOUNT_ID")
BNB_AUTH_ID = os.environ.get("BNB_AUTH_ID")
DESTINATION_ACCOUNT = "1"
BASE_URL = "http://test.bnb.com.bo"
# QRs activos: {qr_id: {"numero": ..., "monto": ..., "gloss": ...}}
qrs_activos = {}

def obtener_token():
    try:
        url = f"{BASE_URL}/ClientAuthentication.API/api/v1/auth/token"
        r = requests.post(url, json={
            "accountId": BNB_ACCOUNT_ID,
            "authorizationId": BNB_AUTH_ID
        }, headers={"Content-Type": "application/json"})
        data = r.json()
        if data.get("success"):
            return data["message"]
        return None
    except:
        return None

def generar_qr(numero, monto, gloss, fn_enviar_imagen, fn_enviar_mensaje):
    try:
        token = obtener_token()
        if not token:
            fn_enviar_mensaje(numero, "❌ Error al conectar con el BNB")
            return

        url = f"{BASE_URL}/QRSimple.API/api/v1/main/getQRWithImageAsync"
        expiracion = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "cache-control": "no-cache"
        }
        body = {
            "currency": "BOB",
            "gloss": gloss,
            "amount": float(monto),
            "singleUse": True,
            "expirationDate": expiracion,
            "additionalData": f"AsistentePersonal - {gloss}",
            "destinationAccountId": DESTINATION_ACCOUNT
        }
        r = requests.post(url, json=body, headers=headers)
        data = r.json()

        if not data.get("success"):
            fn_enviar_mensaje(numero, f"❌ Error BNB: {data.get('message')}")
            return

        qr_id = data["id"]
        qr_bytes = data["qr"]

        # Guardar QR activo
        qrs_activos[qr_id] = {
            "numero": numero,
            "monto": monto,
            "gloss": gloss
        }

        # Enviar imagen QR
        fn_enviar_imagen(numero, qr_bytes, caption=f"💳 *{gloss}*\n💵 Monto: *{monto} Bs*\n⏳ Válido por 24 horas")

        # Arrancar verificador en background
        t = threading.Thread(
            target=_verificar_loop,
            args=(qr_id, fn_enviar_mensaje),
            daemon=True
        )
        t.start()

    except Exception as e:
        fn_enviar_mensaje(numero, f"❌ Error: {e}")

def _verificar_loop(qr_id, fn_enviar_mensaje):
    token = obtener_token()
    if not token:
        return

    url = f"{BASE_URL}/QRSimple.API/api/v1/main/getQRStatusAsync"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "cache-control": "no-cache"
    }

    intentos = 0
    max_intentos = 120  # 120 * 30 seg = 1 hora máximo

    while intentos < max_intentos:
        time.sleep(30)
        try:
            r = requests.post(url, json={"qrId": qr_id}, headers=headers)
            data = r.json()
            status = data.get("statusId")
            info = qrs_activos.get(qr_id)

            if not info:
                break

            if status == 2:  # Pagado
                voucher = data.get("voucherId", "N/A")
                fn_enviar_mensaje(
                    info["numero"],
                    f"✅ *{info['monto']} Bs de {info['gloss']} ya fueron pagados*\n🧾 Voucher: {voucher}"
                )
                del qrs_activos[qr_id]
                break

            elif status == 3:  # Expirado
                fn_enviar_mensaje(
                    info["numero"],
                    f"❌ El QR de *{info['gloss']}* expiró sin ser pagado."
                )
                del qrs_activos[qr_id]
                break

            elif status == 4:  # Error
                fn_enviar_mensaje(
                    info["numero"],
                    f"❌ Error en el QR de *{info['gloss']}*."
                )
                del qrs_activos[qr_id]
                break

        except:
            pass

        intentos += 1

def procesar_cobro(texto):
    """
    Parsea mensajes tipo:
    'cobrar 10 Pago Wally'
    'cobro 50.5 Alquiler enero'
    """
    partes = texto.strip().split(" ", 2)
    if len(partes) < 3:
        return None, None, "❌ Usá: *cobrar [monto] [descripción]*\nEj: *cobrar 10 Pago Wally*"
    try:
        monto = float(partes[1])
        gloss = partes[2]
        return monto, gloss, None
    except:
        return None, None, "❌ El monto debe ser un número. Ej: *cobrar 10.5 Alquiler*"