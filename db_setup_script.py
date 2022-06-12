import sqlite3

con = sqlite3.connect('scores.db')
cur = con.cursor()
try:
    cur.execute(
        "CREATE TABLE scores (user text, date text, score real)"
    )
    con.commit()
except sqlite3.OperationalError:
    print("Table for scores exists")
try:
    cur.execute(
        "CREATE TABLE winners (user text, date text)"
    )
    con.commit()
    # Get all the dates in the table
    date_list = cur.execute("SELECT DISTINCT date from scores ORDER BY date ASC ").fetchall();
    print(date_list)

    for date in date_list:
        print(date)
        day_scores = cur.execute("SELECT * from scores WHERE date = ? ORDER BY score ", [date[0]]).fetchall()
        print(day_scores)
        winner_list = [day_scores[0][0]]
        winner_score = day_scores[0][2]
        if len(day_scores) > 1 :
            i = 1
            next_score = day_scores[i][2]
            next_winner = day_scores[i][0]
            while(winner_score == next_score):
                print(f"winner score{winner_score} next score{next_score}")
                winner_list.append(next_winner)
                i += 1
                next_score = day_scores[i][2]
                next_winner = day_scores[i][0]
        for winner in winner_list:
            print(winner)
            cur.execute("INSERT INTO winners values (?, ?)", [str(winner), str(date[0])])
            con.commit()

except sqlite3.OperationalError:
    print("Table for winners exists")

con.close()


    
