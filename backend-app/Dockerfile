FROM python:3.6

RUN mkdir /app
COPY . /app 

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update; apt install  libcairo2-dev libgirepository1.0-dev -y
RUN pip3 install -r requirements.txt
RUN pip3 install ddtrace cryptography PyMySQL pymysql structlog json-logging
EXPOSE 8000
RUN which flask
RUN which python
RUN ls -l
CMD ["ddtrace-run","python3", "main.py"]
