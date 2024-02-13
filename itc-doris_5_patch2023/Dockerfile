FROM ubuntu:18.04
USER root
# Install dependencies
# PIP - openssl version > 1.1 may be an issue (try older ubuntu images)
RUN apt-get update \
  && apt-get install -y wget gcc make openssl libffi-dev libgdbm-dev libsqlite3-dev libssl-dev zlib1g-dev \
  && apt-get clean

# WORKDIR /tmp/

# Build Python source for doirs
RUN apt-get install -y gdal-bin python-gdal libgdal-dev gawk make tcsh csh wget git tar zip vim build-essential python-pip \
  && pip install fiona shapely scipy html HTMLParser requests fastkml lxml -U pyopenssl matplotlib pyproj


RUN apt-get update \
  && wget -c http://www.fftw.org/fftw-3.2.2.tar.gz \
  && tar -xvf fftw-3.2.2.tar.gz \
  && cd fftw-3.2.2 \
  && ./configure --enable-float \
  && make \
  && make install \
  && cd ~ \
  && git clone https://github.com/LC-SAR/Doris5ITCupdate.git \
  && cd Doris5ITCupdate/doris/doris_core \
  && chmod +x ./configure \
  && ./configure \
  && make \
  && make install \
  && cd ../sar_tools \
  && make \
  && make install \
  && cd ../envisat_tools \
  && make \
  && make install


