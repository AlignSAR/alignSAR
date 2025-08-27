FROM ubuntu:18.04
USER root

# Install dependencies
# PIP - openssl version > 1.1 may be an issue (try older ubuntu images)
RUN apt-get update \
  && apt-get install -y wget gcc make openssl libffi-dev libgdbm-dev libsqlite3-dev libssl-dev zlib1g-dev \
  && apt-get clean

# Install additional dependencies for Doris
RUN apt-get install -y gdal-bin python-gdal libgdal-dev gawk make tcsh csh wget git tar zip vim build-essential python-pip \
  && pip install fiona shapely scipy html HTMLParser requests fastkml lxml -U pyopenssl matplotlib pyproj

# Build FFTW from source
RUN apt-get update \
  && wget -c http://www.fftw.org/fftw-3.2.2.tar.gz \
  && tar -xvf fftw-3.2.2.tar.gz \
  && cd fftw-3.2.2 \
  && ./configure --enable-float \
  && make \
  && make install

# Clone Doris source
RUN cd ~ \
  && git clone https://github.com/LC-SAR/Doris5ITCupdate.git

# === Custom updates to file paths BEFORE compilation ===
# Update doris_main.py: change sys.path.append('/home/username/software/') to '/root/Doris5ITCupdate/'
RUN test -f /root/Doris5ITCupdate/doris/doris_stack/main_code/doris_main.py && \
    sed -i "s|sys\.path\.append(['\"]/home/username/software/['\"])|sys.path.append('/root/Doris5ITCupdate/')|" \
    /root/Doris5ITCupdate/doris/doris_stack/main_code/doris_main.py

# Update doris_config.xml: set <source_path> to /root/Doris5ITCupdate/doris
RUN test -f /root/Doris5ITCupdate/doris/install/doris_config.xml && \
    sed -i "s|<source_path>.*</source_path>|<source_path>/root/Doris5ITCupdate/doris</source_path>|" \
    /root/Doris5ITCupdate/doris/install/doris_config.xml

# Build Doris modules with updated config
RUN cd /root/Doris5ITCupdate/doris/doris_core \
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
RUN chmod +x /root/Doris5ITCupdate/doris/doris_stack/main_code/jobHandlerScript


