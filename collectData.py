#!/usr/bin/python3

import os
import sys
import json
import time
import subprocess
import sqlite3
import logging

# const
AWS = "/usr/bin/aws"
TMPLOG = "/home/nick/src/git/Speedtest/status.json"
IPERF = "/usr/bin/iperf3"

logging.basicConfig(filename='run.log', level=logging.DEBUG)
# Notify the user that the aws ec2 instance is starting, and then open it. Write
# the output to status.json
def launchEC2():
    try:
        logging.info("Launching EC2 instance now:")
        os.system(AWS + " ec2 start-instances --instance-ids i-06611553665cca9ac > " + TMPLOG)
        logging.info("Loading, please wait:")

        # From here, keep circling until the ec2 instance has finished loading and is now running
        # If the server is already on, this will break out after 1 iteration
        os.system(AWS + " ec2 describe-instance-status --instance-ids i-06611553665cca9ac > " + TMPLOG)
        with open(TMPLOG, "r") as fp:
            status = json.load(fp)

        while True:
            if status["InstanceStatuses"] == []:
                logging.info("echo Amazon is still loading this instance, please wait")
                time.sleep(2)
                os.system(AWS + " ec2 describe-instance-status --instance-ids i-06611553665cca9ac > " + TMPLOG)
                with open(TMPLOG, "r") as fp:
                    status = json.load(fp)
            else:
                logging.info("echo Amazon EC2 instance has finished loading")
                break

        # Give the ec2 some time to launch the iperf3 -s command (grace period of 5 seconds)
        logging.info("Allow EC2 instance to launch iperf3 server")
        time.sleep(5)
    except Exception:
        logging.exception("Could not launch EC2 server")
        sys.exit(0)

def collectData():
    answer = "not set"
    try:
        # Create the command needed for the local machine to communicate to the EC2 server. Line 55-56
        # is used to retrieve the IP address of the ec2 instance (changes every time it is launched)
        ip_addr = subprocess.check_output(AWS + " ec2 describe-instances --instance-ids i-06611553665cca9ac --query Reservations[0].Instances[0].PublicIpAddress", shell=True).strip()
        # command = IPERF + " -c " + output.decode("utf-8") + " -J"

        # WILL CAUSE FUNCTION TO FAIL: remove after test
        command = IPERF + " -c " + ip_addr.decode("utf-8") + " -J"

        # Simutaneously run the command and collect information
        answer = subprocess.check_output(command, shell=True).decode("utf-8")
        results = json.loads(answer)

        # We focus on collecting 3 fields - upload speed, download speed, and time
        upload_speed = float(results["end"]["sum_sent"]["bits_per_second"]) / 1000000
        download_speed = float(results["end"]["sum_received"]["bits_per_second"]) / 1000000
        duration = results["end"]["sum_received"]["seconds"]
        timestamp = results["start"]["timestamp"]["time"]
        return (timestamp, duration, upload_speed, download_speed)
    except Exception:
        logging.exception(answer)
        return ()

def ingestDataIntoSQL(data):

    # Testing purposes only, will need to remove later on
    # print("Upload speed: " + str(upload_speed))
    # print("Download speed: " + str(download_speed))
    # print("Time: " + str(Time))
    # print("Duration: " + str(duration))

    # Create the table initially - comment out after first run
    # c.execute("""create table test_measurements(
    #             test_id integer PRIMARY KEY,
    #             time text,
    #             duration text,
    #             upload_speed integer,
    #             download_speed integer)""")

    if len(data) == 0:
        os.system("echo Error detected at data collection, no new entry will be recorded")
        return

    # Connect to our database speedData.db
    conn = sqlite3.connect('/home/nick/src/git/Speedtest/speedData.db')
    c = conn.cursor()
    c.execute("INSERT INTO test_measurements (time, duration, upload_speed, download_speed) VALUES (?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

def closeEC2():
    logging.info("Closing EC2 instance after latent period")
    os.system(AWS + " ec2 stop-instances --instance-ids i-06611553665cca9ac > " + TMPLOG)

def main():
    launchEC2()
    ingestDataIntoSQL(collectData())
    closeEC2()

if __name__ == "__main__":
    main()
