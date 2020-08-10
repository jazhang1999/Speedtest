# Speedtest
Code to measure the upload/download speed of my computer using iperf3. This project inovlves a variety of tools that we wanted to experiment with, so we designed the layout and functionality of the project around those tools. While the actual code is written in Python, we also wrote a couple shell scripts to communicate with tools like crontab.

# Topics
The project uses 3 items to work correctly:
* Amazon Web Services (AWS) - We used an EC2 instance to host an iperf3 server, so that my computer could communicate with it and get relevent statistics (upload / download speed)
* Crontab - used to automate the data collection. We have it set to collect ever 15 minutes. Can be toggled on and off
* SQLite3 - We used this to store our data. As of right now, no way of representing said data.

# iPerf3
I chose to use a modified version of iPerf3, which allowed for the results to be saved as a log file, a feature that was not available in the standard version of iperf3 that can be obtained from `sudo apt get install iperf3`

# Setting up the EC2 Instance
This was most likely the most complicated step of the entire project. We used AWS CLI on Windows Subsystem for Linux (WSL), which made the process a little easier since it allowed for certain steps, like creating a key-pair and configuring security settings for the EC2 instance, to be done over command line. Youtube videos were the best walkthrough for this type of task, as well as Amazon's own setup manual on their website:
* Eukreda!: https://www.youtube.com/watch?v=sLtf7Sx8lsQ&t=1791s
* Amazon Setup Page: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

__In addition to creating the EC2 instance, there were a couple configurations in the .aws folder in the home directory.__ 
* credentials: Swap it out with the lines that AWS CLI gave me (We used AWS Educate, so this may be special to us)
* config: Set the `output = json` and `region = us-east-1`. This will allow output for aws commands to show up in json format (which is much easier to parse than a formatted table or hard text), but more importantly sets the correct region of our instance. 

__Notes on the EC2 Instance:__
* We created an Ubuntu EC2 instance, since we have the most experience using that distribution of linux than any other. 
* There is only ever one instance. This project does not delete old or create new instances. This for optimizing the code, but also for making sure we do not have to continuously reinstall iperf3 and rewrite the crontab on every potentially new instance created

# Crontab
The only crontab command we run on the local machine is `*/15 * * * * /home/nick/src/git/Speedtest/runner.sh > /tmp/run.log 2>&1` on my personal machine. It calls the runner.sh, which triggers the python code to communicate with the EC2 instance and grab measurement data, every 15 minutes. Since everything crontab executes is backend, we write the output to a log so that in the case of an error, we can see exactly what went wrong. For debugging and checking purposes only. It is important to note that crontab only runs a __shell__ script every 15 minutes. This is done because we want to control whether the program will keep running or not in the shell script, not the crontab. More on that below 

The command that is run in the EC2 instance is `@reboot iperf3 -s > /tmp/run.log 2>&1`. This will launch an iperf3 server that the local machine can communicate with upon being launched. Once again, any output will be written to a log file for checking purposes

# Shell Scripts
We use 2 shell scripts to control the running of the data collection. 

The first one, __runner.sh__, will actually call the python program that facillitates the data collection. To decide whether or not to collect, it uses a marker file named `marker` to check to see if it should run or not. If it can find it, the program will run. If not, nothing will be done. In this way, we can turn the program on and off without having to constantly modify the crontab. 
```
#!/bin/bash

FILE=/home/nick/src/git/Speedtest/marker

if test -f "$FILE"; then
    /usr/bin/python3 /home/nick/src/git/Speedtest/newCollectData.py
fi
```
For the actual toggling, here is the script __toggleRunner.sh__ that adds in or removes the marker file. 
```
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
```
Toggling on will look like this:
```
nick@DESKTOP-IU7TM26:~/src/git/Speedtest$ ./toggleRunner.sh
Script is inactive, start it up? (y/n)y
```
While toggling off will look like this:
```
nick@DESKTOP-IU7TM26:~/src/git/Speedtest$ ./toggleRunner.sh
Script is active, shut it down? (y/n)y
```
In this way, we allow the user to activate/deactivate this program without having to do anything too complicated

# Graphing using Python and SQL
![1](https://github.com/jazhang1999/Speedtest/blob/master/Figures/Figure1.png?raw=true)
