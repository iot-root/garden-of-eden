FROM python:3.9-slim

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

RUN apt-get update && \
    apt-get install -y gcc make

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --force-reinstall --no-cache-dir --no-binary :all: RPi.GPIO

COPY run.py .

# Run mqtt.py when the container launches
# CMD ["python", "run.py"]