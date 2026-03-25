import gspread
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from playwright.async_api import async_playwright

load_dotenv()

CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS')
SHEET_NAME = os.getenv('SHEET_NAME')

def conectar_planilha():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive',
    ]

    cred = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scope)
    client = gspread.authorize(cred)

    planilha = client.open(SHEET_NAME)
    aba = planilha.sheet1

    #cria um cabeçalho se a planilha estiver vazia

    if not aba.row_values(1):
        aba.append_row(
            ['Setor',
             'Modalidade de Ingresso',
             'Preço (R$)',
             'Disponibilidade',
             'Data de Rastreio',
            ],
            value_input_option='USER_ENTERED'
        )
        print('Cabeçalho criado com sucesso')
    return aba

