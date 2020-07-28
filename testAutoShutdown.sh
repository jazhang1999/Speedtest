#!/bin/bash

echo "Running script to determine if shutdown is necessary"
exitStatus=$(/usr/bin/python3 /home/nick/src/git/Speedtest/checkLastUpdated.py)

if test $exitStatus == 1; then
    echo "Shutdown command goes here"   
fi
