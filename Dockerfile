FROM python:3.7.4
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
WORKDIR /app/web
