#!/usr/bin/python
# Older version of data collection. Does everything inside the program, no crontab used
import os
import json
import time
import subprocess
import sqlite3
import sys
import pdb
from datetime import datetime

# Connect to our database speedData.db
conn = sqlite3.connect('speedData.db')
c = conn.cursor()

# Retrieve command-line arguments:
c.execute("create table " + str(sys.argv[1]) + " (test_id integer PRIMARY KEY, time text, duration text, intervals integer, upload_speed integer, download_speed integer)")

intervals = int(sys.argv[2])

# Notify the user that the aws ec2 instance is starting, and then open it. Write
# the output to status.json 
os.system("echo Launching EC2 instance now:")
os.system("aws ec2 start-instances --instance-ids i-06611553665cca9ac > status.json")
os.system("echo Loading, please wait:")

# From here, keep circling until the ec2 instance has finished loading and is now running
# If the server is already on, this will break out after 1 iteration
os.system("aws ec2 describe-instance-status --instance-ids i-06611553665cca9ac > status.json")
with open("status.json", "r") as fp:
        status = json.load(fp)

while True:
    if status["InstanceStatuses"] == []:
        os.system("echo Working on it, please wait")
        time.sleep(2)
        os.system("aws ec2 describe-instance-status --instance-ids i-06611553665cca9ac > status.json")
        with open("status.json", "r") as fp:
            status = json.load(fp)
    else:
        os.system("echo EC2 instance has finished loading")
        break

# Give the ec2 some time to launch the iperf3 -s command (grace period of 5 seconds)
os.system("echo Allow EC2 instance to launch iperf3 server")
time.sleep(5)

# Create the command needed for the local machine to communicate to the EC2 server. Line 55-56
# is used to retrieve the IP address of the ec2 instance (changes every time it is launched)
output = subprocess.check_output("aws ec2 describe-instances --instance-ids i-06611553665cca9ac --query Reservations[0].Instances[0].PublicIpAddress", shell=True).strip()
command = "iperf3 -c " + output.decode("utf-8") + " -J"

while intervals > 0:
    # Simutaneously run the command and collect information 
    results = json.loads(subprocess.check_output(command, shell=True).decode("utf-8"))

    # We focus on collecting 3 fields - upload speed, download speed, and time
    upload_speed = float(results["end"]["sum_sent"]["bits_per_second"]) / 1000000
    download_speed = float(results["end"]["sum_received"]["bits_per_second"]) / 1000000
    duration = results["end"]["sum_received"]["seconds"]
    Time = results["start"]["timestamp"]["time"]

    # Testing purposes only, will need to remove later on
    print("Upload speed: " + str(upload_speed))
    print("Download speed: " + str(download_speed))
    print("Intervals: " + str(intervals))
    print("Time: " + str(Time))
    print("Duration: " + str(duration))


    # Create the table initially - comment out after first run
    # c.execute("""create table test_measurements(
    #              test_id integer PRIMARY KEY,
    #              time text,
    #              duration text,
    #              intervals integer,
    #              upload_speed integer,
    #              download_speed integer)""")

    c.execute("INSERT INTO " + sys.argv[1] + " (time, duration, intervals, upload_speed, download_speed) VALUES (?, ?, ?, ?, ?)", (Time, duration, intervals, upload_speed, download_speed))
    intervals = intervals - 1 
    time.sleep(10)

conn.commit()
conn.close()

os.system("echo Closing EC2 instance after latent period")
os.system("aws ec2 stop-instances --instance-ids i-06611553665cca9ac > status.json")





