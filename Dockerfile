FROM python:3.7.1
RUN mkdir /app
ADD . /app
RUN apt-get install pipenv && pipenv install --system
WORKDIR /app/web