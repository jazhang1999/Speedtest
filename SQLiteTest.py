#!/usr/bin/python3

import sqlite3

conn = sqlite3.connect('speedData.db')

c = conn.cursor()
c.execute("""create table betaMeasurements(
            date text PRIMARY KEY,
            upload_speed integer,
            download_speed integer)""")
            
conn.commit()

conn.close()
