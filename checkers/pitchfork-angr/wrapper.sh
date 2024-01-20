#!/bin/bash
source venv/bin/activate
python3 wrapper.py $@
RESULT=$?
deactivate
exit $RESULT