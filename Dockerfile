FROM python:3.7
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
#RUN pipenv install --system
WORKDIR /app/web