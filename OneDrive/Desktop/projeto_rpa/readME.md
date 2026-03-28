# 🤖 Projeto RPA - Monitoramento de Ingressos (Eventim + Google Sheets + Telegram)

Este projeto automatiza a coleta, organização e notificação de ingressos disponíveis para eventos (ex: shows) utilizando **Playwright**, **Google Sheets** e **Telegram**.

---

# 📁 Estrutura do Projeto

```
PROJETO_RPA/
│
├── bots/
│   ├── bot-eventim.py       # Coleta dados do site (Playwright)
│   ├── bot-planilhas.py     # Envia dados CSV → Google Sheets
│   └── bot-telegram.py      # Envia alertas via Telegram
│
├── dados_csv/               # Armazena os arquivos CSV gerados
│
├── .env                     # Variáveis de ambiente (credenciais)
├── credentials.json         # Credenciais Google Service Account
├── crontab                  # Agendamento das execuções
├── docker-compose.yml       # Orquestração do container
├── Dockerfile               # Build da imagem Docker
├── requirements.txt         # Dependências do projeto
```

---

# ⚙️ Como funciona o fluxo

O sistema segue um pipeline simples e eficiente:

```
[ bot-eventim ]
        ↓
(gera CSV)
        ↓
[ bot-planilhas ]
        ↓
(atualiza Google Sheets)
        ↓
[ bot-telegram ]
        ↓
(envia alerta de ingressos disponíveis)
```

---

# 🕷️ bot-eventim.py (Coleta com Playwright)

Responsável por:

* Acessar o site da Eventim
* Identificar eventos disponíveis
* Entrar no primeiro evento encontrado
* Coletar:

  * setor
  * tipo de ingresso
  * preço
  * disponibilidade
* Gerar um arquivo `.csv` com os dados

### Destaques:

* Usa **Playwright (Chromium headless)**
* Faz parsing dinâmico da página
* Organiza dados prontos para consumo

---

# 📊 bot-planilhas.py (Integração com Google Sheets)

Responsável por:

* Ler o CSV gerado
* Conectar ao Google Sheets via API
* Atualizar a planilha:

  * limpa dados antigos
  * envia novos dados formatados

### Requisitos:

* `credentials.json` (Service Account)
* Variável `SHEET_NAME` no `.env`

---

# 📲 bot-telegram.py (Notificações)

Responsável por:

* Ler dados da planilha
* Filtrar ingressos disponíveis
* Formatar mensagem
* Enviar alerta via Telegram

### Funcionalidades:

* Exibe até 15 ingressos
* Formatação amigável (HTML)
* Mostra data da coleta
* Evita enviar mensagens vazias

---

# 🔐 Variáveis de Ambiente (.env)

Exemplo:

```
GOOGLE_CREDENTIALS=credentials.json
SHEET_NAME=NomeDaSuaPlanilha

TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

---

# 🐳 Docker

## Build

```
docker-compose build
```

## Subir container

```
docker-compose up -d
```

---

# ⏰ Agendamento com Cron

O projeto usa `cron` dentro do container para execução automática.

### Exemplo configurado:

```
30 22 * * * cd /app && python bots/bot-eventim.py && python bots/bot-planilhas.py && python bots/bot-telegram.py >> /var/log/cron.log 2>&1
```

### Isso significa:

* Executa **todos os dias às 22:30**
* Roda os bots **em sequência**
* Só executa o próximo se o anterior tiver sucesso

---

# 📄 Logs

Para acompanhar execução:

```
docker logs -f bots-automacao
```

ou dentro do container:

```
cat /var/log/cron.log
```

---

# ⚠️ Observações Importantes

* O `bot-eventim` deve rodar apenas **1x por dia**
* O uso de `&&` evita execução em cascata em caso de erro
* Playwright roda em modo headless no container

---

# 🚀 Possíveis melhorias futuras

* Histórico de preços
* Alertas apenas para mudanças
* Integração com banco de dados
* Dashboard web
* Suporte a múltiplos eventos

---

# 🧠 Resumo

Este projeto implementa um fluxo completo de RPA:

* 🕷️ Scraping (Playwright)
* 📊 Processamento (CSV + Sheets)
* 🔔 Notificação (Telegram)
* ⏰ Automação (Cron + Docker)

---
