FROM python:3.11-bullseye

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y tzdata locales build-essential libpq-dev libpcre3-dev libffi-dev git gettext curl wget nano postgresql-client

RUN mkdir /app
WORKDIR /app
COPY . /app/
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "core.wsgi:application", "-c", "deploy/backend/gunicorn.py"]



