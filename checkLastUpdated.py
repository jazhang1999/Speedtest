
import os
import time

# Get last modified time
st = os.stat('/home/nick/src/git/Speedtest/temp.txt')
modTime = st.st_mtime
currTime = time.time()

if (currTime - modTime > 300):
    print(1) # System has been running too long - shut it down
else:
    print(0) # System can stay on
    
# This is code for the AWS EC2 (Ubuntu) instance. It is a safeguard against
# the program running for too long. The code is moved to the other instance
# vi ssh (operation)
