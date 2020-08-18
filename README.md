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

(Insert chart here)

For the sake of clarity, I have included all of the required files for both the AWS EC2 instance and the local computer in this git repository. I will also include crontab commands right here, so that you can just copy and paste into your crontab. Use the chart to decide which files you should move from your local computer to your EC2 instance. 
__============================================================================= Local Computer =============================================================================
__Local computer's crontab:__ `*/15 * * * * /home/nick/src/git/Speedtest/runner.sh > /tmp/run.log 2>&1`

__runner.sh and toggleRunner.sh__ are both used in conjunction with the local computer's crontab listed above to automate the process of data retrieval. By

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
This is very much a work in progress. While the code for reading from the sqlite3 database is good, the formatting is very off. This will be addressed at a later date.

![1](https://github.com/jazhang1999/Speedtest/blob/master/Figures/Figure1.png?raw=true)
