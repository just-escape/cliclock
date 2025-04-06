FROM python:3.11-slim

WORKDIR /app

COPY static static
COPY fixtures.json .
COPY manage.py .

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY cliclock cliclock
COPY scenario scenario

EXPOSE 8080

RUN python manage.py migrate
RUN python manage.py loaddata fixtures.json

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "cliclock.wsgi:application"]