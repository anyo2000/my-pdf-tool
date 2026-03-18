#!/bin/bash
cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

(while ! curl -s http://127.0.0.1:8080 > /dev/null 2>&1; do sleep 0.5; done; open http://127.0.0.1:8080) &
python3 app.py
