#!/bin/bash

sudo fswebcam -d /dev/video0 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520192042_1.jpg
sudo fswebcam -d /dev/video2 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520192042_2.jpg
