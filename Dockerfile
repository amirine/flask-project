FROM python:slim

RUN useradd flaskblog

WORKDIR /home/flaskblog

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY blog.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP blog.py

RUN chown -R flaskblog:flaskblog ./
USER flaskblog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]
#docker run --name flaskblog -d -p 8000:5000 --rm --env-file .env flaskblog:latest
#docker build -t flaskblog:latest .