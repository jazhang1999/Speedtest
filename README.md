# Speedtest
Code to measure the upload/download speed of my computer using iperf3. This project inovlves a variety of tools that we wanted to experiment with, so we designed the layout and functionality of the project around those tools.

# Topics
The project uses 3 items to work correctly:
* Amazon Web Services (AWS) - We used an EC2 instance to host an iperf3 server, so that my computer could communicate with it and get relevent statistics (upload / download speed)
* Crontab - used to automate the data collection. We have it set to collect ever 15 minutes. Can be toggled on and off
* SQLite3 - We used this to store our data. As of right now, no way of representing said data.

# Setting up the EC2 Instance
This was most likely the most complicated step of the entire project. We used AWS CLI on Windows Subsystem for Linux (WSL), which made the process a little easier since it allowed for certain steps, like creating a key-pair and configuring security settings for the EC2 instance, to be done over command line. Youtube videos were the best walkthrough for this type of task, as well as Amazon's own setup manual on their website:
* Eukreda!: https://www.youtube.com/watch?v=sLtf7Sx8lsQ&t=1791s
* Amazon Setup Page: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html
