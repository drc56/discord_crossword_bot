# /bin/python3
import datetime
import logging
import re
import sqlite3
from pathlib import Path

from discord.ext import commands, tasks

TOKEN = Path('secret_token.txt').read_text()
db_con = sqlite3.connect('scores.db')
bot = commands.Bot(command_prefix='!')

def determine_date() -> str:
    """The NYT does crossword resets on 10PM EST on weekdays and 6PM EST on weekends.
    So a score after that time is assumed to be a puzzle for the next day
    """
    date = datetime.datetime.now()
    if date.weekday() > 4:
        if date.time() >= datetime.time(18,0,0):
            return str(date.date() + datetime.timedelta(days=1))
        else:
            return str(date.date()) 
    else:
        if date.time() >= datetime.time(22,0,0):
            return str(date.date() + datetime.timedelta(days=1))
        else:
            return str(date.date()) 

def get_word_games_chan_id() -> id:
    for chan in bot.get_all_channels():
        if chan.name == 'word-games':
            return chan

@tasks.loop(hours=1)
async def remind_for_scores():
    date = datetime.datetime.now()
    if date.weekday() > 4:
        if date.time() >= datetime.time(17,0,0):
            chan = get_word_games_chan_id()
            await chan.send("REMINDER: Complete and submit crossword scores")
    else:
        if date.time() >= datetime.time(21,0,0):
            chan = get_word_games_chan_id()
            await chan.send("REMINDER: Complete and submit crossword scores")

@bot.command(name='mini-leader', help="Responds with today's leaderboard")
async def handle_leaderboard(ctx):
    cur = db_con.cursor()
    date = determine_date()
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
        date = determine_date()

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
        date = determine_date()

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