from playwright.sync_api import sync_playwright
import csv
import os
from datetime import datetime
import time

URL_PATH = "https://www.eventim.com.br/artist/rush2027/"
HOME_PATH = "https://www.eventim.com.br"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_DADOS = os.path.join(BASE_DIR, "dados_csv")

os.makedirs(PASTA_DADOS, exist_ok=True)

def encontrar_shows(page):
    page.goto(URL_PATH, wait_until="domcontentloaded")
    time.sleep(3)
    page.wait_for_selector('[data-qa="event-listing-item"]')
    
    eventos = []
    shows = page.locator('[data-qa="event-listing-item"]')

    for i in range(shows.count()):
        show = shows.nth(i)
        try:
            cidade = show.locator(".event-listing-city").inner_text().strip()
            dia = show.locator('[data-qa="event-date-day"]').inner_text().strip()
            mes = show.locator('[data-qa="event-date-month-year"]').inner_text().strip()
            data = f"{dia}-{mes}"
            status = show.locator('[data-qa="list-event-state"]').inner_text().strip()
            link = show.locator("a").first.get_attribute("href")

            eventos.append({
                "cidade": cidade,
                "data": data,
                "status": status,
                "link": HOME_PATH + link
            })
        except Exception as e:
            print(f"Erro ao capturar evento {i}:", e)
            
    return eventos

def selecionar_venda_geral(page):
    seletor = page.locator('select[name="promo_id"]')
    seletor.wait_for()
    time.sleep(3)
    seletor.select_option(label="VENDA GERAL")
    page.wait_for_selector('[data-qa="tickettype"]')

def coletar_ingressos(page):
    tickets = []
    elementos = page.locator(".pc-list-detail, .ticket-type-list")
    setor_atual = None
    data_coleta = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for i in range(elementos.count()):
        el = elementos.nth(i)
        classes = el.get_attribute("class") or ""

        if "event-list-head" in classes:
            try:
                setor_atual = el.locator(".pc-list-category span").text_content().strip()
            except:
                setor_atual = "DESCONHECIDO"

        elif "ticket-type-list" in classes:
            items = el.locator('[data-qa="tickettype"]')
            for j in range(items.count()):
                item = items.nth(j)
                try:
                    nome = item.get_attribute("data-tt-name")
                    preco_str = item.locator('[data-qa="tickettypeItem-price"]').text_content()
                    preco = formatar_preco(preco_str)
                    
                    indisponivel = item.locator('[data-qa="ticket-type-unavailable"]').count() > 0
                    disponivel = not indisponivel

                    tickets.append({
                        "setor": setor_atual,
                        "nome": nome,
                        "preco": preco,
                        "disponivel": disponivel,
                        "coletado em": data_coleta
                    })
                except Exception as e:
                    pass
                    
    return tickets

def formatar_preco(preco):
    return preco.replace("R$", "").replace("\xa0", "").strip()

def formatar_data(data):
    return data.replace(" ", "").replace(".", "-")

def salvar_csv(evento, ingressos):
    nome_arquivo = f"{evento['cidade'].lower().replace(' ', '-')}-{formatar_data(evento['data'])}.csv"
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    with open(caminho, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["setor", "nome", "preco", "disponivel", "coletado em"])
        writer.writeheader()
        writer.writerows(ingressos)
    print(f"Ficheiro CSV salvo em: {caminho}")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_default_timeout(60000)

        eventos = encontrar_shows(page)
        
        if not eventos:
            print("Nenhum show encontrado na página.")
            browser.close()
            return

        # Foca apenas no primeiro evento da lista
        primeiro_evento = eventos[0]
        print(f"\n=== ACESSANDO APENAS O PRIMEIRO SHOW: {primeiro_evento['cidade']} ===")
        
        try:
            page.goto(primeiro_evento["link"], wait_until="domcontentloaded")
            selecionar_venda_geral(page)
            ingressos = coletar_ingressos(page)
            salvar_csv(primeiro_evento, ingressos)
        except Exception as e:
            print(f"Erro ao extrair {primeiro_evento['cidade']}: {e}")

        print("\n=== PROCESSO FINALIZADO ===")
        browser.close()

if __name__ == "__main__":
    main()