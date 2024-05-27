#!/bin/bash

python -m venv venv &&
source venv/bin/activate &&
sudo systemctl enable pigpiod && 
sudo systemctl start pigpiod &&
python ./api/run.py