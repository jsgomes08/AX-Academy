import os
import gspread
import requests
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

nome_credencial = os.getenv('GOOGLE_CREDENTIALS', 'credentials.json')
if not os.path.isabs(nome_credencial):
    CREDENTIALS_FILE = os.path.join(BASE_DIR, nome_credencial)
else:
    CREDENTIALS_FILE = nome_credencial

SHEET_NAME = os.getenv('SHEET_NAME')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def conectar_planilha():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    cred = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    client = gspread.authorize(cred)
    return client.open(SHEET_NAME) 

def formatar_preco(valor):
    try:
        if isinstance(valor, (int, float)):
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if isinstance(valor, str) and "." in valor and "," not in valor:
            valor_float = float(valor)
            return f"{valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return str(valor)
    except:
        return str(valor)

def enviar_mensagem_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() 
        print("Mensagem enviada com sucesso ao Telegram!")
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Telegram: {e}")

def verificar_planilha_e_notificar():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Erro: Credenciais do Telegram ausentes!")
        return

    print("Conectando ao Google Sheets...")
    try:
        planilha = conectar_planilha()
        
        aba = planilha.get_worksheet(0) 
        nome_da_aba = aba.title
        
        registros = aba.get_all_records()
        
        if not registros:
            print(f"A aba '{nome_da_aba}' está vazia.")
            return

        disponiveis = [
            linha for linha in registros 
            if str(linha.get('Disponibilidade', '')).strip().lower() in ['sim', 'true']
        ]

        if not disponiveis:
            print("Nenhum ingresso disponível no momento.")
            return

        mensagem = f" <b>Ingressos encontrados para Show do Rush em {nome_da_aba}</b> \n\n"
        
        limite_exibicao = 15
        for ing in disponiveis[:limite_exibicao]:
            setor = ing.get('Setor', 'Desconhecido')
            modalidade = ing.get('Modalidade de Ingresso', 'Desconhecida')
            preco_formatado = formatar_preco(ing.get('Preço (R$)', '0,00'))
            
            mensagem += f"📍 <b>{setor}</b>\n🎟️ {modalidade} | 💰 R$ {preco_formatado}\n\n"

        if len(disponiveis) > limite_exibicao:
            mensagem += f"<i>... e mais {len(disponiveis) - limite_exibicao} ingressos disponíveis! Verifique a planilha completa.</i>\n\n"

        data_coleta = disponiveis[0].get('Data de Rastreio', 'Data não informada')
        mensagem += f"🕒 <i>Informações coletadas em {data_coleta}</i>"

        print(f"Enviando notificação para o evento {nome_da_aba}...")
        enviar_mensagem_telegram(mensagem)

    except Exception as e:
        print(f"Erro durante a leitura da planilha ou envio: {e}")

if __name__ == "__main__":
    verificar_planilha_e_notificar()