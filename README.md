# Speedtest with AWS EC2 instance
Code to measure the upload/download speed of my computer using iperf3. This project inovlves a variety of tools that I wanted to experiment with, so the layout and functionality of the project was designed around those tools. While the actual code is written in Python, I also wrote a couple shell scripts to handle automating the process (it would run automatically instead of manually running a script to collect data)

I wrote this code to test the network speed in different parts of my house, to prove that the my room in the house had the worst connection. While that turned out to be ultimately not true (there were even worse areas) I still really enjoyed the creation of this project and the experience I now have working with the tools I used.

__Update__ - You will need your own AWS account and Key-pair to be able to run this project. I also hard-coded some specific parameters into my code, so anyone that wants to run this code will also need to change some constants within the source code as well

# Topics
The project uses 3 items to work correctly:
* __Amazon Web Services (AWS)__ - I used an EC2 instance to host an iperf3 server, so that my computer could communicate with it and get relevent statistics (upload / download speed) I do not have a regular account (used a Student account) so my experiences may vary from someone who has the full suite of features that Amazon offers.
* __SQLite3__ - I wanted to have a way to collect the data I retrieved. With my version of iperf3, the client (my local computer) can retrieve important information like upload speed and download speed as part of a `.json` file. Parsing that information and putting it into a sqlite table was a good way to not only store the data, but to also later graph it later on down the track (more on that later)
* __Crontab__ - After making sure that data could be retrieved and stored, I wanted a way to automate the process, so that the computer would consistently be able to collect good information without me having to run the code manually periodically over that period of time. Setting up a Crontab file on the client side (my computer) was a good way to do this. I also created one on the server side (AWS EC2 instance) so that it would be able to shut down automatically if something went wrong. 

# Blueprint of the Project

![1](https://github.com/jazhang1999/Speedtest/blob/master/Figures/NewChart.png?raw=true)

For the sake of clarity, I have included all of the required files for both the AWS EC2 instance and the local computer in this git repository. I will also include crontab commands right here, so that you can just copy and paste into your crontab. Use the chart to decide which files you should move from your local computer to your EC2 instance.

__======================================= Local Machine =======================================__

__Local computer's crontab:__ `*/15 * * * * /home/nick/src/git/Speedtest/runner.sh > /tmp/run.log 2>&1`

__connectEC2.sh__ is a way for the user to connect to the EC2 instance in order to test or configure the server end of iperf3. It takes the ip address of the EC2 instance (changes every time when launched, so make sure you have the AWS console open). For example, a way to launch is `./connectEC2.sh 123.456.7890`. Also note that I have an absolute path to the key pair needed to access the EC2 instance, which a different user will not have. That must be switched out with the absolute path of the user's key. There may be a prompt that shows up when first running this, just say yes and the server should connect. Any other problems must be resolved through AWS

__runner.sh and toggleRunner.sh__ are both used in conjunction with the local computer's crontab listed above to automate the process of data retrieval. As displayed above, crontab will run runner.sh every 15 minutes. However, that just means that this program will just run without stop, or when the user exits in one way or the other. We do not want that. That is why toggleRunner.sh is a script that the user runs to tell runner.sh to either run the data retrieval or do nothing. Runner.sh relies on a __marker file__ named `marker` in order to do any work:
```
#!/bin/bash

FILE=/home/nick/src/git/Speedtest/marker

if test -f "$FILE"; then
    /usr/bin/python3 /home/nick/src/git/Speedtest/collectData.py
fi
```
toggleRunner.sh either removes the marker file (do not collect data) or adds in the marker file (start collecting data). In this way, the user can control when or when not to collect data without having to modify crontab every time they want to turn something on or off. 

__collectData.py__ is the program called periodically by runner. It works with __status.json__ and __speedData.db__ (sqlite3) in order to collect data in these steps:
* Launch the EC2 instance of a specified process ID. I have mine currently hard-coded, so the user will have to switch it out for theirs. 
* __status.json__ is used to track the status of the EC2 instance: whether it is booting up, has stopped, or is still running. 
* Once it is confirmed that the EC2 instance is up and running, a iperf3 request is made to connect, and we begin getting measurements. This process usually takes around 10 seconds, although it can be configurable. More details inside source code of __collectData.py__
* Select pieces of data from this measurement are then inserted as a row entry into the `test_measurements` table of __speedData.db__ 
* Then we send a command to close down the EC2 instance. Again, some things are hard-coded and will have to be changed by the user


__==================================== Amazon EC2 Instance ====================================__

__Amazon EC2 Crontab:__

`@reboot nohup /home/ubuntu/iperfStart.sh`

`@reboot sleep 300; /home/ubuntu/testAutoShutdown.sh >/home/ubuntu/test.log 2>&1 &`

__iperfStart.sh__ is the script that is run upon the EC2 instance starting up. It essentially launches the iperf server to listen for any client. I did not use the default version of iperf3, rather I used a modified version for this project to effectively achieve its objective. Details are down below. In the diagram above, __iperf3__ is the downloaded package that must be referenced rather than the normal iperf3 to launch that server. I also configured __iperf3__ to also generate a log file, which will be very important later on.

__testAutoShutdown.sh__ and __checkLastUpdated.py__ are safeguards for the EC2 instance not shutting down. Previously, I mentioned that the last step of data collection was to shut down the EC2 instance via the client side (the local computer) of the process. However, there are cases where there will be errors (usually I/O from the testing I did) communicating with the server and telling it to shut down, meaning that the EC2 instance will be left on when it should not be. Given that Amazon's pricing model with AWS is dictated by how much you use their service, this is definetely not something that you want to happen. 

Thereby, __testAutoShutdown.sh__ runs the python program __checkLastUpdated.py__, which will check whether that log file iperf3 created has changed within the last 5 minutes. If it has not, then it will signal to __testAutoShutdown.sh__, which will force the EC2 instance to shut down automatically. 

# Notes on iPerf3
Originally I used the default version of iperf3 that you can get, i.e the one that comes from running `sudo apt get install iperf3`. This works fine for the purpose of displaying the data. However, there is no way to save this after the initial run in a straightforward way, meaning that I would have to either find some workaround or use a different tool. 

Thereby, I chose to use a modified version of iperf3, that would be able to write the resulting output to a logfile. You can clone git clone the repo into your directory and then have to change which iperf3 version will be running: https://github.com/esnet/iperf

# Notes on EC2 Instance
This was most likely the most complicated step of the entire project. We used AWS CLI on Windows Subsystem for Linux (WSL), which made the process a little easier since it allowed for certain steps, like creating a key-pair and configuring security settings for the EC2 instance, to be done over command line. Youtube videos were the best walkthrough for this type of task, as well as Amazon's own setup manual on their website:
* Eukreda!: https://www.youtube.com/watch?v=sLtf7Sx8lsQ&t=1791s
* Amazon Setup Page: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

__In addition to creating the EC2 instance, there were a couple configurations in the .aws folder in the home directory.__ 
* credentials: Swap it out with the lines that AWS CLI gave (We used AWS Educate, so this may be special to us)
* config: Set the `output = json` and `region = us-east-1`. This will allow output for aws commands to show up in json format (which is much easier to parse than a formatted table or hard text), but more importantly sets the correct region of our instance. 

__Notes on the EC2 Instance:__
* We created an Ubuntu EC2 instance, since we have the most experience using that distribution of linux than any other. 
* There is only ever one instance. This project does not delete old or create new instances. This for optimizing the code, but also for making sure we do not have to continuously reinstall iperf3 and rewrite the crontab on every potentially new instance created

# Graphing using Python and SQL
This is very much a work in progress. While the code for reading from the sqlite3 database is good, the formatting is very off. This will be addressed at a later date.

![1](https://github.com/jazhang1999/Speedtest/blob/master/Figures/Figure1.png?raw=true)
