import sqlite3
with sqlite3.connect('urls.db') as conn:
    cursor = conn.cursor()
    for i in range(1,10000000):
        cursor.execute("INSERT INTO WEB_URL(URL) VALUES ('aHR0cDovLw==')")
