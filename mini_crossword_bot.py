# /bin/python3
import datetime
import logging
import re
import sqlite3

from discord.ext import commands

# TODO store these in an environment file and load it in
TOKEN = 'OTc3MTg5MTU2NTE2MTQ3MjUw.G8uDQB.m8WBM2He1MYoSLb1A4_PBuH65cjxKpMPy3dKDE'
db_con = sqlite3.connect('scores.db')
bot = commands.Bot(command_prefix='!')

@bot.command(name='mini-leader', help="Responds with today's leaderboard")
async def handle_leaderboard(ctx):
    cur = db_con.cursor()
    date = str(datetime.date.today())
    leader_cmd = 'SELECT * FROM scores WHERE date = ? ORDER BY score'
    cur.execute(leader_cmd, [date])
    rows = cur.fetchall()
    msg = f'{date} Leaderboard'
    place = 1
    for row in rows:
        msg += f'\n{place}. {row[0]} : {row[2]}'
        place += 1
    logging.info(msg)
    await ctx.send(msg)

@bot.command(name='mini-score', help="Allows you to submit your score for today in format m:ss")
async def handle_mini_score(ctx):
    cur = db_con.cursor()
    m = re.search('!mini-score\s([0-9]+):([0-9][0-9])', ctx.message.content)
    if m is None:
        # TODO figure out a good way to error handle here
        logging.info(f"Invalid message format: {ctx.message.content}")
        await ctx.send("Error with score message format, try again, must be `m:ss`")
        return
    else:
        time = int(m.group(1)) * 60 + int(m.group(2))
        user = str(ctx.message.author)
        date = str(datetime.date.today())

        # Check if the user already has a score
        check_cmd = 'SELECT * from scores WHERE user = ? AND date = ?'
        cur.execute(check_cmd, [user, date])
        rows = cur.fetchall()
        if not rows:
            insert_cmd = 'INSERT into scores values (?, ?, ?)'
            cur.execute(insert_cmd,[user, date, time])
            db_con.commit()
            logging.info(f'{user} score is {time} for date {date}')
            await ctx.send(f"Score recorded for {user} for {date}")
        else:
            # (TODO) Figure out how to handle this error
            logging.info(f"Score submitted today {ctx.message.content}")
            await ctx.send(f"{user}, you already submitted a score today")

@bot.command(name='mini-correct', help="Correct your score if you made a mistake submitting today")
async def handle_mini_correct(ctx):
    cur = db_con.cursor()
    m = re.search('!mini-correct\s([0-9]+):([0-9][0-9])', ctx.message.content)
    if m is None:
        # TODO figure out a good way to error handle here
        logging.info(f"Invalid message format: {ctx.message.content}")
        await ctx.send("Error with score message format, try again, must be `m:ss`")
        return
    else:
        time = int(m.group(1)) * 60 + int(m.group(2))
        user = str(ctx.message.author)
        date = str(datetime.date.today())

        # Check if the user already has a score
        check_cmd = 'SELECT * from scores WHERE user = ? AND date = ?'
        cur.execute(check_cmd, [user, date])
        rows = cur.fetchall()

        if not rows:
            await ctx.send(f"You don't have a score to correct today {user}")
        else:
            delete_cmd = 'DELETE from scores WHERE user = ? AND date = ?'
            cur.execute(delete_cmd,[user,date])
            insert_cmd = 'INSERT into scores values (?, ?, ?)'
            cur.execute(insert_cmd,[user, date, time])
            db_con.commit()
            logging.info(f'{user} score is {time} for date {date}')
            await ctx.send(f"Score corrected for {user} for {date}")

def main():
    logging.basicConfig(filename='crossword_bot.log', level=logging.DEBUG)
    logging.info('Starting bot')
    bot.run(TOKEN)

if __name__ == '__main__':
    main()