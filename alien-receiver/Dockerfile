FROM python:3.8-alpine

# Install needed system packages
RUN apk update && apk add \
    gcc \
    g++ \
    python3-dev \
    musl-dev \
    libffi-dev

# Create app dir and add in requirements
RUN mkdir /srv/alien-receiver/
WORKDIR /srv/alien-receiver/
ADD requirements.txt .

# Install requirements
RUN pip install -r requirements.txt

# Install app
ADD receiver.py .
ENTRYPOINT ["python3", "-u", "receiver.py"]
