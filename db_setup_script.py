import sqlite3

con = sqlite3.connect('scores.db')
cur = con.cursor()
try:
    cur.execute(
        "CREATE TABLE scores (user text, date text, score real)"
    )
    con.commit()
    con.close()
except sqlite3.OperationalError:
    con.close()
