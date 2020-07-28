#!/usr/bin/python

import os
import json
import time
import subprocess
import sqlite3
from datetime import datetime

# const
AWS = "/usr/bin/aws"
TMPLOG = "/home/nick/src/git/Speedtest/status.json"

# Connect to our database speedData.db
conn = sqlite3.connect('/home/nick/src/git/Speedtest/speedData.db')
c = conn.cursor()

# Notify the user that the aws ec2 instance is starting, and then open it. Write
# the output to status.json 
os.system("echo Launching EC2 instance now:")
os.system(AWS + " ec2 start-instances --instance-ids i-06611553665cca9ac > " + TMPLOG)
os.system("echo Loading, please wait:")

# From here, keep circling until the ec2 instance has finished loading and is now running
# If the server is already on, this will break out after 1 iteration
os.system(AWS + " ec2 describe-instance-status --instance-ids i-06611553665cca9ac > " + TMPLOG)
with open(TMPLOG, "r") as fp:
        status = json.load(fp)

while True:
    if status["InstanceStatuses"] == []:
        os.system("echo Working on it, please wait")
        time.sleep(2)
        os.system(AWS + " ec2 describe-instance-status --instance-ids i-06611553665cca9ac > " + TMPLOG)
        with open(TMPLOG, "r") as fp:
            status = json.load(fp)
    else:
        os.system("echo EC2 instance has finished loading")
        break

# Give the ec2 some time to launch the iperf3 -s command (grace period of 5 seconds)
os.system("echo Allow EC2 instance to launch iperf3 server")
time.sleep(5)

# Create the command needed for the local machine to communicate to the EC2 server. Line 55-56
# is used to retrieve the IP address of the ec2 instance (changes every time it is launched)
output = subprocess.check_output(AWS + " ec2 describe-instances --instance-ids i-06611553665cca9ac --query Reservations[0].Instances[0].PublicIpAddress", shell=True).strip()
command = "/usr/bin/iperf3 -c " + output.decode("utf-8") + " -J"

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
print("Time: " + str(Time))
print("Duration: " + str(duration))

# Create the table initially - comment out after first run
# c.execute("""create table test_measurements(
#             test_id integer PRIMARY KEY,
#             time text,
#             duration text,
#             upload_speed integer,
#             download_speed integer)""")

c.execute("INSERT INTO test_measurements (time, duration, upload_speed, download_speed) VALUES (?, ?, ?, ?)", (Time, duration, upload_speed, download_speed))

conn.commit()
conn.close()

os.system("echo Closing EC2 instance after latent period")
os.system(AWS + " ec2 stop-instances --instance-ids i-06611553665cca9ac > " + TMPLOG)



