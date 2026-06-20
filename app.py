@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.json
    try:
        entry = data.get("entry", [])
        if not entry: return "ok", 200
        changes = entry[0].get("changes", [])
        if not changes: return "ok", 200
        value = changes[0].get("value", {})
        messages = value.get("messages", [])
        if not messages: return "ok", 200
        mensaje = messages[0]
        numero = mensaje["from"]
        tipo = mensaje["type"]

        if tipo == "text":
            texto = mensaje["text"]["body"]
            respuesta = procesar_mensaje(numero, texto)
            enviar_mensaje(numero, respuesta)

        elif tipo == "audio":
            audio_id = mensaje["audio"]["id"]
            texto = procesar_audio(audio_id)
            if texto:
                enviar_mensaje(numero, f"🎤 _{texto}_")
                respuesta = procesar_mensaje(numero, texto)
                enviar_mensaje(numero, respuesta)
            else:
                enviar_mensaje(numero, "❌ No pude entender el audio.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
    return "ok", 200