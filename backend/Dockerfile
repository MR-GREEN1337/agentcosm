FROM python:3.13-slim

ENV PYTHONUNBUFFERED=true
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc libcairo2-dev

COPY /requirements.txt .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

COPY /src/ ./src/

ENV PYTHONPATH=/app
ENV PORT=8000

# Expose envs
RUN export $(cat .env | xargs)

EXPOSE 8000

# Create an entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

CMD ["entrypoint.sh"]
