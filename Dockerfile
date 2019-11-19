FROM python:3.7-slim-buster

MAINTAINER Till Schulte

COPY requirements.txt requirements.txt

# RUN apk add gcc libc-dev build-base gtk-doc git autoconf automake libtool make cmake
# RUN apk add libev-dev dumb-init freetype freetype-dev libstdc++ jpeg-dev gcc libjpeg-turbo-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev harfbuzz-dev fribidi-dev
RUN apt-get update && apt-get install libjpeg-dev libev-dev \
    libfreetype6-dev libraqm-dev dumb-init -y \
# -- Installation with custom repository --
    && pip install --no-cache-dir -r requirements.txt --extra-index-url=https://s.chulte.de/pip/ \
# -- This is a shitty solution, but I cant do it better --
    && pip uninstall pillow -y && rm -rf /usr/local/lib/python3.7/site-packages/Pillow* \
    && rm -rf /usr/local/lib/python3.7/size-packages/PIL/ \
    && apt-get install --no-install-recommends gcc libc-dev -y \
    && pip install --no-cache-dir https://files.pythonhosted.org/packages/5b/bb/cdc8086db1f15d0664dd22a62c69613cdc00f1dd430b5b19df1bea83f2a3/Pillow-6.2.1.tar.gz \
    && apt-get remove gcc libc-dev -y \
    && apt-get autoremove -y \
    && apt-get clean

ENTRYPOINT ["/usr/bin/dumb-init"]