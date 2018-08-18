FROM python:3
MAINTAINER Eric H Chang "eric_h_chang@trend.com.tw"

COPY requirements.txt /root/

RUN cd /root \
      && pip install -r requirements.txt \
      && cd /
