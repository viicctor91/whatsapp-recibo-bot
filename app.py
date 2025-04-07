from flask import Flask, request, jsonify
import requests
from recibo_generator import gerar_recibo
from whatsapp_utils import enviar_mensagem_com_pdf
import os

app = Flask(__name__)

VERIFY_TOKEN = "seutokenseguro123"  # Use esse mesmo token no painel da Meta

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode and token:
            if token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return "Token de verificação inválido", 403

    if request.method == "POST":
        data = request.get_json()
        print("Recebido:", data)

        try:
            mensagens = data["entry"][0]["changes"][0]["value"]["messages"]
            for msg in mensagens:
                if msg["type"] == "audio":
                    audio_id = msg["audio"]["id"]
                    numero = msg["from"]

                    # Baixar áudio
                    audio_url = f"https://graph.facebook.com/v17.0/{audio_id}"
                    headers = {
                        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}"
                    }
                    response = requests.get(audio_url, headers=headers)
                    audio_response = requests.get(response.json()["url"], headers=headers)

                    with open("audio.ogg", "wb") as f:
                        f.write(audio_response.content)

                    # Transcrever com Whisper
                    import whisper
                    model = whisper.load_model("base")
                    result = model.transcribe("audio.ogg")
                    texto = result["text"]

                    # Extrair dados do texto
                    import re
                    valor = re.search(r"(\\d{1,3}(\\.\\d{3})*,\\d{2}|\\d+)", texto).group()
                    nome = re.search(r"para (.*?) cpf", texto, re.IGNORECASE).group(1).strip()
                    servico = re.search(r"servi[cç]o (.*)", texto, re.IGNORECASE).group(1).strip()

                    # Gerar PDF
                    caminho_pdf = gerar_recibo(nome=nome, valor=valor, servico=servico)

                    # Enviar PDF
                    enviar_mensagem_com_pdf(numero, caminho_pdf)

        except Exception as e:
            print("Erro:", e)

        return "ok", 200

# CORREÇÃO PARA FUNCIONAR NO RENDER:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

