FROM debian:jessie-slim

LABEL Author="Rafael Gomes <madrafael.gsilva@gmail.com>"

RUN apt-get update && apt-get upgrade -y

RUN apt-get update && apt-get install -y \
  python-dev \
  libmysqlclient-dev \
  python2.7 \
  gearman-job-server \
  make \
  build-essential \
  mysql-client-5.5 && apt-get clean && apt-get autoclean

COPY ./start.sh /start.sh
RUN chmod 755 /*.sh

RUN mkdir -p /var/log/gearmand

RUN mkdir /opendb

COPY ./all-schemas /opendb

WORKDIR /opendb

RUN python2.7 get-pip.py

RUN python2.7 -m pip install -r requirements.txt

CMD ["/bin/bash", "/start.sh"]