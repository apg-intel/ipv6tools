FROM python:2.7
MAINTAINER Josh Porter <joshporter1@gmail.com>

RUN apt-get update && \
  apt-get -qq -y install tcpdump graphviz imagemagick python-gnuplot python-crypto python-pyx && \
  apt-get clean

# copy just requirements.txt to avoid doing bundle on every file change
COPY ./requirements.txt /src/
WORKDIR /src
RUN pip install -r requirements.txt
COPY . /src

CMD ["python", "server.py"]
EXPOSE 5000
