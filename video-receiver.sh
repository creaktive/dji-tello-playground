#!/bin/sh
# https://tellopilots.com/threads/tello-video-web-streaming.455/#post-13986
exec ffplay -probesize 32 -i udp://@:11111 -framerate 30
