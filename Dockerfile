FROM python:3.11

RUN mkdir /app
WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev \
    postgresql-client

ENV PYTHONUNBUFFERED 1

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000