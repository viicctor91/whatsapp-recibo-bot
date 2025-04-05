
import requests
import os

def enviar_mensagem_com_pdf(numero, caminho_pdf):
    url = f"https://graph.facebook.com/v17.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}"
    }

    # Enviar documento
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "document",
        "document": {
            "filename": caminho_pdf,
            "caption": "Aqui está o seu recibo.",
            "link": ""  # Substituir por link público se necessário
        }
    }

    response = requests.post(url, headers=headers, json=data)
    print(response.json())
