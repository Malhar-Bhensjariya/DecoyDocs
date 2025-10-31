import sqlite3
conn = sqlite3.connect('honeypot.db')
c = conn.cursor()
for row in c.execute("SELECT * FROM logs ORDER BY time DESC"):
    print(row)
conn.close()
