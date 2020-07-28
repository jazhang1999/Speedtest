
import numpy as np
#############################################
import matplotlib 
matplotlib.use("Agg")
#############################################
import matplotlib.pyplot as plt
import sqlite3

# Connect to the SQLite3 database
conn = sqlite3.connect('/home/nick/src/git/Speedtest/speedData.db')
conn.row_factory = lambda cursor, row: row[0]
cursorObj = conn.cursor()

# data to plot
n_groups = len((cursorObj.execute('select * from test_measurements')).fetchall())
time = (cursorObj.execute('select time from test_measurements')).fetchall()
upload = (cursorObj.execute('select upload_speed from test_measurements')).fetchall()
download = (cursorObj.execute('select download_speed from test_measurements')).fetchall()

# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8

rects1 = plt.bar(index, list(upload), bar_width,
alpha=opacity,
color='g',
label='Upload')

rects2 = plt.bar(index + bar_width, list(download), bar_width,
alpha=opacity,
color='r',
label='Download')

plt.xlabel('Time')
plt.ylabel('Speed in Mb/s')
plt.title('Upload & Download Speeds')
plt.xticks(index + bar_width, list(time))
plt.legend()

plt.tight_layout()
plt.savefig("./test.png")

