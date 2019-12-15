FROM python:3.8-alpine

# Make app directory
RUN mkdir /srv/listkeeper/
WORKDIR /srv/listkeeper/

# Copy and install requirements
RUN apk update && apk add \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev

COPY requirements.txt .
RUN pip3 install -r requirements.txt && pip3 install gunicorn

# Install rest of app
COPY . .
ENV DJANGO_SETTINGS_MODULE listkeeper.production_settings

# Handle static files
RUN SECRET_KEY=temp python manage.py collectstatic --noinput

# Commands to run with
ENV PORT 80
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 listkeeper.wsgi:application
