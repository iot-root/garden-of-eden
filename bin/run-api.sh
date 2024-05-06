python -m venv venv
source venv/bin/activate
sudo systemctl start pigpiod
python ./api/run.py