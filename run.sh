#!/bin/bash

# Settings
RUNPORT=5000
BINDIP=0.0.0.0

# Export the variables
export FLASK_APP=nfgame.py
export NFGAME_SETTINGS=nfgame.cfg

# If the database does not exists, create it.
if [ ! -f nfgame.db ]; then
  python -m flask initdb
fi

if [ ! -f nfgame.cfg ]; then
  echo "Please copy nfgame.cfg-example to nfgame.cfg and edit the options!"
  exit 1
fi

# If working in debug mode
if [[ $1 == 'start' ]]; then
  if [[ $2 == 'debug' ]]; then
    export FLASK_DEBUG=1
    python -m flask run --host=$BINDIP --port=$RUNPORT
  else
    if [ -f twistd.pid ]; then
       echo "Game is still running."
       echo "Stop the game first, or remove the file twistd.pid"
      exit 1
    fi
    twistd web --port $RUNPORT --logfile=nfgame.log --wsgi=nfgame.app
    echo "Game is started!"
    echo "Have fun!"
  fi
fi

if [[ $1 == 'stop' ]]; then
  kill `cat twistd.pid`
  echo "Game is over!"
fi
