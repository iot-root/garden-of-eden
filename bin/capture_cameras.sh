#!/bin/bash

sudo fswebcam -d /dev/video0 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520182015_1.jpg
sudo fswebcam -d /dev/video2 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520182015_2.jpg
