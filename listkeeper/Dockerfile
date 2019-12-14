FROM python:3.8-alpine

# Make app directory
RUN mkdir /srv/listkeeper/
WORKDIR /srv/listkeeper/

# Copy and install requirements
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
COPY requirements.txt .
RUN pip3 install -r requirements.txt && pip3 install gunicorn

# Install rest of app
COPY . .
COPY listkeeper/production_settings.py listkeeper/local_settings.py

# Commands to run with
ENV PORT 80
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 listkeeper.wsgi:application
