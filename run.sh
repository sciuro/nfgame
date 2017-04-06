#!/bin/bash

# Settings
RUNPORT=5000
BINDIP=0.0.0.0

# Export the variables
export FLASK_APP=nfgame.py
export NFGAME_SETTINGS=nfgame.cfg

# If working in debug mode
if [[ $1 == 'debug' ]]; then
  export FLASK_DEBUG=1
else
  export FLASK_DEBUG=0
fi

# If the database does not exists, create it.
if [ ! -f nfgame.db ]; then
  python -m flask initdb
fi

if [ ! -f nfgame.cfg ]; then
  echo "Please copy nfgame.cfg-example to nfgame.cfg and edit the options!"
else
  python -m flask run --host=$BINDIP --port=$RUNPORT
fi
