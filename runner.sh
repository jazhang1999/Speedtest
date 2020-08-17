#!/bin/bash

FILE=/home/nick/src/git/Speedtest/marker

if test -f "$FILE"; then
    /usr/bin/python3 /home/nick/src/git/Speedtest/collectData.py
fi
