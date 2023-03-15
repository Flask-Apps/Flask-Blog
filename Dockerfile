FROM python:3.10-alpine

ENV FLASK_APP iblog.py
ENV FLASK_CONFIG docker


RUN adduser -D iblog

WORKDIR /home/iblog
COPY boot.sh ./
RUN chmod +x /home/iblog/boot.sh

USER iblog

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/docker.txt

COPY app app
COPY migrations migrations
COPY iblog.py config.py ./

# runtime configuration
EXPOSE 5000
ENTRYPOINT [ "./boot.sh" ]


