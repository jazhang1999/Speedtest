#!/bin/bash

FILE=/home/nick/src/git/Speedtest/marker

if test -f "$FILE"; then
    read -n1 -p "Script is active, shut it down? (y/n)" doit 
    case $doit in
        y|Y) echo ; rm 'marker' ;;
        n|N) echo ; echo 'Okay, script will continue running' ;;
    esac
else 
    read -n1 -p "Script is inactive, start it up? (y/n)" doit 
    case $doit in
        y|Y) echo ; touch 'marker' ;;
        n|N) echo ; echo 'okay, script will stay dormant';; 
    esac

fi
