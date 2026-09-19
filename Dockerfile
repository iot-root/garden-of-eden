# Garden of Eden — container image for the REST API and the MQTT service.
#
# GPIO is NOT accessed in-container: both processes talk to a pigpiod that runs
# on the Pi host (set PIGPIO_HOST/PIGPIO_PORT). This keeps the image free of
# privileged hardware access while still driving real pins. See docker-compose.yml.
FROM python:3.11-slim

# fswebcam is needed for the camera endpoints; tini for clean signal handling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends fswebcam tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PIGPIO_HOST=host.docker.internal \
    PIGPIO_PORT=8888 \
    PYTHONUNBUFFERED=1

EXPOSE 5000

ENTRYPOINT ["/usr/bin/tini", "--"]
# Default to the REST API; docker-compose overrides the command for the MQTT service.
CMD ["python", "run.py"]
