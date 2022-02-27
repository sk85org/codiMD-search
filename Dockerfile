FROM python:3.10.2
USER root

RUN apt-get update
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools

RUN python -m pip install flask
RUN python -m pip install psycopg2
WORKDIR /app
COPY . /app
CMD ["python","/app/server.py"]