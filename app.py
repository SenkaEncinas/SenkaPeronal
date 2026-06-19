from flask import Flask, request
import requests

app = Flask(__name__)

WHATSAPP_TOKEN = "EAAtk2S9icJIBRwZAzeTpfvEmOI7S6r0qrX86f0StPsEgZAAyN6r45iOnZCmzqWRd1usBNf5dEuQQ52BwzyNZAdsy0zaMZAxJ2r7JtA2D02ZAcOizADUUnnyQnBsoh3TkKqV3VKepxrB5FDPQptCLZCZChMCPCMv9Qi6GZCu0bxyGKSs66w3lt7yvcRSxqLxntxA0yiF9HCaWocqz7ZBssam3LoTijlkQIyDLPL0O1VGnOwKUw6iLXttSinFPt4OZBkIhVzbvKKrSWZAkrcvZCcKGUfHZCuGQZDZD"
PHONE_NUMBER_ID = "1107700089101313"
VERIFY_TOKEN = "senka_verify_2024"

def enviar_mensaje(numero, texto):
    url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(url, headers=headers, json=body)

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    modo = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if modo == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.json
    try:
        mensaje = data["entry"][0]["changes"][0]["value"]["messages"][0]
        numero = mensaje["from"]
        tipo = mensaje["type"]

        if tipo == "text":
            texto = mensaje["text"]["body"]
            respuesta = f"Recibí tu mensaje: {texto}"
            enviar_mensaje(numero, respuesta)
    except:
        pass
    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)