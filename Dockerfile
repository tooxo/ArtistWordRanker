FROM python:3.9-slim-buster

MAINTAINER Till Schulte

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get --no-install-recommends install libjpeg-dev libev-dev \
    libfreetype6-dev libraqm-dev dumb-init libc-dev gcc git -y \
# -- Installation with custom repository --
    && pip install --compile --no-cache-dir -r requirements.txt \
# -- This is a shitty solution, but I cant do it better --
    && apt-get remove gcc libc-dev -y \
    && apt-get autoremove -y \
    && apt-get clean

WORKDIR /usr/src/app/
COPY . .
CMD ["/bin/bash", "-c", "export $(grep -v '^#' .env | xargs -d '\n') && python3 server_async.py"]