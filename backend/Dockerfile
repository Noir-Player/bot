FROM python:3.12-alpine AS builder

WORKDIR /backend

RUN apk add --no-cache git build-base

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]