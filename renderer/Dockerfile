FROM python:3.13-slim

ENV PYTHONUNBUFFERED=true
WORKDIR /app

RUN apt-get update && apt-get -y install libpq-dev gcc libcairo2-dev

COPY /requirements.txt .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PORT=8001
ENV $(cat .env | xargs)

EXPOSE 8001

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
