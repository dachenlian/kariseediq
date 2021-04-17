FROM python:3.7.9
ADD requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
ADD . /app
WORKDIR /app/web
