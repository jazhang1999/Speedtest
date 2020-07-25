# Speedtest
Code to measure the upload/download speed of my computer using iperf3. This project inovlves a variety of tools that we wanted to experiment with, so we designed the layout and functionality of the project around those tools.

# Topics
The project uses 3 items to work correctly:
* Amazon Web Services (AWS) - I used an EC2 instance to host an iperf3 server, so that my computer could communicate with it and get relevent statistics (upload / download speed)
* Crontab - used to automate the data collection. We have it set to collect ever 15 minutes. Can be toggled on and off
* SQLite3 - I used this to store data. As of right now, no way of representing said data
