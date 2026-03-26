import gspread
import os
import csv
from datetime import datetime
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
PASTA_DADOS = os.path.join(BASE_DIR, "dados_csv")

def conectar_planilha():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']
    cred = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    client = gspread.authorize(cred)
    return client.open(SHEET_NAME) 

def processar_csv():
    planilha = conectar_planilha()
    
    arquivos_csv = [f for f in os.listdir(PASTA_DADOS) if f.endswith('.csv')]
    
    if not arquivos_csv:
        print("Nenhum arquivo CSV encontrado na pasta.")
        return

    nome_arquivo = arquivos_csv[0]
    caminho_csv = os.path.join(PASTA_DADOS, nome_arquivo)
    novo_titulo = nome_arquivo.replace(".csv", "")
    
    aba = planilha.get_worksheet(0) 
    
    if aba.title != novo_titulo:
        print(f"Renomeando aba para '{novo_titulo}'")
        aba.update_title(novo_titulo)

    print("Atualizando planilha com últimos dados coletados:")
    aba.clear() 

    dados_completos = [[
        'Setor', 'Modalidade de Ingresso', 'Preço (R$)', 
        'Disponibilidade', 'Data de Rastreio'
    ]]

    with open(caminho_csv, mode='r', encoding='utf-8') as file:
        leitor_csv = csv.DictReader(file)
        for linha in leitor_csv:
            status_disponivel = "Sim" if linha.get('disponivel') == 'True' else "Não"
            nova_linha = [
                linha.get('setor', ''),
                linha.get('nome', ''),
                linha.get('preco', ''),
                status_disponivel,
                linha.get('coletado em', '')
            ]
            dados_completos.append(nova_linha)

    if len(dados_completos) > 1:
        aba.append_rows(dados_completos, value_input_option='USER_ENTERED')
        print(f"Upload concluído! Dados atualizados em '{novo_titulo}'.")
    else:
        print("O arquivo CSV está vazio ou sem dados válidos.")

if __name__ == "__main__":
    processar_csv()