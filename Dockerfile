FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY static static
COPY manage.py .
COPY fixtures.json .

COPY cliclock cliclock
COPY scenario scenario

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "cliclock.wsgi:application"]