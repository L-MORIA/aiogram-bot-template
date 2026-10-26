FROM python:3.12-slim

WORKDIR /app

# Сначала только зависимости — слой кэшируется, пока requirements.txt не меняется
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Каталог для SQLite-файла (том docker-compose) + непривилегированный пользователь
RUN mkdir -p /app/data \
    && useradd --create-home botuser \
    && chown -R botuser:botuser /app
USER botuser

CMD ["python", "bot.py"]
