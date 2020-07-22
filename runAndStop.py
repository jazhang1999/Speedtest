#!/usr/bin/python

import os
import json
import time
import subprocess
import sqlite3
from datetime import datetime

os.system("echo Launching EC2 instance now:")
os.system("aws ec2 start-instances --instance-ids i-06611553665cca9ac > status.json")
os.system("echo Loading, please wait:")

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


os.system("echo Allow EC2 instance to launch iperf3 server")
time.sleep(5)
output = subprocess.check_output("aws ec2 describe-instances --instance-ids i-06611553665cca9ac --query Reservations[0].Instances[0].PublicIpAddress", shell=True).strip()
command = "iperf3 -c " + output.decode("utf-8") + " -J"
# os.system(command)

results = json.loads(subprocess.check_output(command, shell=True).decode("utf-8"))
upload_speed = results["end"]["sum_sent"]["bits_per_second"]
download_speed = results["end"]["sum_received"]["bits_per_second"]
time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
print("Time initiated: " + str(time))
print("Upload speed: " + str(upload_speed))
print("Download speed: " + str(download_speed))

conn = sqlite3.connect('speedData.db')
c = conn.cursor()

c.execute("""create table betaMeasurements(
            date text PRIMARY KEY,
            upload_speed integer,
            download_speed integer)""")

c.execute("INSERT INTO betaMeasurements VALUES (?, ?, ?)", (time, upload_speed, download_speed))
# c.execute("""create table betaMeasurements (date text, download_speed integer, upload_speed integer)""")

conn.commit()
conn.close()

os.system("echo Closing EC2 instance after latent period")
os.system("aws ec2 stop-instances --instance-ids i-06611553665cca9ac > status.json")





