FROM python:3.7-slim-buster

MAINTAINER Till Schulte

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get --no-install-recommends install libjpeg-dev libev-dev \
    libfreetype6-dev libraqm-dev dumb-init libc-dev gcc -y \
# -- Installation with custom repository --
    && pip install --compile --no-cache-dir -r requirements.txt --extra-index-url=https://s.chulte.de/pip/ \
# -- This is a shitty solution, but I cant do it better --
    && apt-get remove gcc libc-dev -y \
    && apt-get autoremove -y \
    && apt-get clean

WORKDIR /usr/src/app/
COPY . .

ENTRYPOINT ["/usr/bin/dumb-init"]