FROM python:3.12-alpine AS builder

WORKDIR /backend


COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "app.py"]