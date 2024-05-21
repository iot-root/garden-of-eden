#!/bin/bash

fswebcam -d /dev/video0 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520211208_1.jpg
fswebcam -d /dev/video2 -r 2500x1900 -S 2 -F 2 /tmp/capture_20240520211208_2.jpg
