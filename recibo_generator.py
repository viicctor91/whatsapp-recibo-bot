
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def gerar_recibo(nome, valor, servico):
    arquivo = f"recibo_{nome.replace(' ', '_')}.pdf"
    c = canvas.Canvas(arquivo, pagesize=A4)
    width, height = A4

    # Logo
    c.drawImage("logo.png", 50, height - 120, width=150, preserveAspectRatio=True, mask='auto')

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 100, "RECIBO")

    # Texto do recibo
    c.setFont("Helvetica", 12)
    texto = f"Recebi de Minas Calçados a importância de R${valor} referente a {servico}."
    c.drawString(50, height - 160, texto)

    # Assinatura
    c.drawString(50, height - 210, f"Assinatura: {nome}")

    # Data
    data = datetime.now().strftime("%d/%m/%Y")
    c.drawString(50, height - 260, f"Data: {data}")

    c.save()
    return arquivo
