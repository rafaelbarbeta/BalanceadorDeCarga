FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY serviceA.py .
COPY pub pub

CMD [ "python3", "serviceA.py"]