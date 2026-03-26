# Imagem base: Python 3.12 versão enxuta (~200MB vs ~1GB da versão completa)
FROM python:3.12-slim

# Não gera arquivos .pyc desnecessários dentro do container
ENV PYTHONDONTWRITEBYTECODE=1

# Garante que o print() aparece imediatamente nos logs, sem buffer
ENV PYTHONUNBUFFERED=1

# Diz ao Playwright onde instalar os navegadores
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Instala as bibliotecas do sistema que o Chromium precisa para rodar
# --no-install-recommends: não instala pacotes extras desnecessários
# rm -rf /var/lib/apt/lists/*: limpa o cache do apt para reduzir o tamanho da imagem
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 libpango-1.0-0 \
    libpangocairo-1.0-0 libx11-xcb1 cron procps \
    && rm -rf /var/lib/apt/lists/*

# Define /app como pasta de trabalho dentro do container
# Todo comando seguinte vai rodar a partir daqui
WORKDIR /app

# Copia PRIMEIRO só o requirements.txt — antes do restante do código
# Motivo: o Docker cacheia cada etapa. Se o código mudar mas o requirements.txt
# não mudar, ele reaproveita o cache e não reinstala tudo do zero
COPY requirements.txt .

# Instala as dependências Python
# --no-cache-dir: não guarda cache do pip, reduz tamanho da imagem
RUN pip install --no-cache-dir -r requirements.txt

# Instala apenas o Chromium (não precisa de Firefox nem WebKit)
RUN playwright install chromium --with-deps

# Agora copia o restante do código para dentro do container
COPY . .

# Copia o arquivo de agendamentos para o local que o cron lê
COPY crontab /etc/cron.d/bots

# Define as permissões corretas e registra os agendamentos
RUN chmod 0644 /etc/cron.d/bots && crontab /etc/cron.d/bots

# Cria o arquivo de log (o cron exige que ele exista antes de escrever)
RUN touch /var/log/cron.log

# Comando que roda quando o container inicia:
# 1. cron: inicia o serviço de agendamento
# 2. tail -f: fica "olhando" o log em tempo real
#    sem isso o container encerraria imediatamente após iniciar o cron
CMD ["cron", "-f"]