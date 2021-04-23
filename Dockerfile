FROM debian:jessie

LABEL Author="Rafael Gomes <madrafael.gsilva@gmail.com>"

RUN apt-get update && apt-get upgrade -y

RUN apt-get update && apt-get install -y build-essential python-dev \
  libapache2-mod-wsgi-py3 \
  libmysqlclient-dev \
  python2.7 \
  # supervisor \
  gearman-job-server \
  wget \
  vim \
  make \
  build-essential \
  mysql-client-5.5 && apt-get clean

COPY ./start.sh /start.sh
RUN chmod 755 /*.sh
# RUN mkdir -p /etc/supervisor/conf.d
# ADD ./supervisor-gearmand.conf /etc/supervisor/conf.d/gearmand.conf
# ADD ./supervisor-workeropendb.conf /etc/supervisor/conf.d/workerdbd.conf

RUN mkdir -p /var/log/gearmand

RUN mkdir /opendb

COPY ./all-schemas /opendb

WORKDIR /opendb

# RUN gearmand -d

RUN python2.7 get-pip.py

RUN python2.7 -m pip install -r requirements.txt

# CMD ["gearmand", "-d"]
CMD ["/bin/bash", "/start.sh"]
# CMD ["python2.7", "worker_allschemas.py"]
