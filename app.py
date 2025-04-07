from flask import Flask, request, jsonify
import requests
from recibo_generator import gerar_recibo
from whatsapp_utils import enviar_mensagem_com_pdf
import os

app = Flask(__name__)

VERIFY_TOKEN = "seutokenseguro123"

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
        print("🔔 Recebido:", data)

        try:
            mensagens = data["entry"][0]["changes"][0]["value"].get("messages", [])
            for msg in mensagens:
                if msg["type"] == "audio":
                    audio_id = msg["audio"]["id"]
                    numero = msg["from"]
                    print(f"🎧 Áudio recebido de {numero}")

                    # Baixar áudio
                    audio_url = f"https://graph.facebook.com/v17.0/{audio_id}"
                    headers = {
                        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}"
                    }
                    response = requests.get(audio_url, headers=headers)
                    audio_info = response.json()
                    print("🔗 URL do áudio:", audio_info.get("url"))

                    audio_response = requests.get(audio_info["url"], headers=headers)

                    with open("audio.ogg", "wb") as f:
                        f.write(audio_response.content)
                    print("📥 Áudio salvo como audio.ogg")

                    # Transcrição
                    import whisper
                    model = whisper.load_model("base")
                    result = model.transcribe("audio.ogg")
                    texto = result["text"]
                    print("📝 Texto transcrito:", texto)

                    # Extração de dados
                    import re
                    valor = re.search(r"(\\d{1,3}(\\.\\d{3})*,\\d{2}|\\d+)", texto)
                    nome = re.search(r"para (.*?) cpf", texto, re.IGNORECASE)
                    servico = re.search(r"servi[cç]o (.*)", texto, re.IGNORECASE)

                    if not (valor and nome and servico):
                        print("⚠️ Não foi possível extrair todos os dados do texto.")
                        return "ok", 200

                    valor = valor.group()
                    nome = nome.group(1).strip()
                    servico = servico.group(1).strip()

                    print(f"✅ Dados extraídos:\n  Nome: {nome}\n  Valor: {valor}\n  Serviço: {servico}")

                    # Gerar PDF
                    caminho_pdf = gerar_recibo(nome=nome, valor=valor, servico=servico)
                    print(f"📄 PDF gerado: {caminho_pdf}")

                    # Enviar recibo
                    enviar_mensagem_com_pdf(numero, caminho_pdf)
                    print("📤 Recibo enviado!")

        except Exception as e:
            print("❌ Erro geral:", e)

        return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
