#!/bin/sh
source venv/bin/activate

while true; do
    flask deploy
    if [[ "$?" == "0" ]]; then
        break
    fi
    echo Deploy command failed, retrying in 5 secs...
    sleep 5
done

# --access-logfile -: log http requests to stdout, `-` meaning
# make gunicorn process take over the process running the boot.sh
# because when the process ends the container ends as well so docker
# pays special attention to that process
exec gunicorn -b 0.0.0.0:5000 --access-logfile - --error-logfile - iblog:app