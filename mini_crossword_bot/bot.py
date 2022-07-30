# /bin/python3

import asyncio
import datetime
from distutils.command.build import build
import logging
import re
import sqlite3
import pytz
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands, tasks

# Globals & Configs
TOKEN = Path('secret_token.txt').read_text()
<<<<<<< HEAD
g_bot = commands.Bot(command_prefix='!')
=======
bot = commands.Bot(command_prefix='!')
>>>>>>> master
ROLE_NAME = "crossword_players"
GUILD_NAME = "Queue Tip Bandits"

# Helper functions and data types
@dataclass
class LeaderboardEntry:
    """ Data submitted by a user to store in leaderboard
    """
    user: str = ""
    date: str = ""
    time: int = 0

def determine_date(today: bool = True) -> str:
    """The NYT does crossword resets on 10PM EST on weekdays and 6PM EST on weekends.
    So a score after that time is assumed to be a puzzle for the next day
    """
    et = pytz.timezone('US/Eastern')
    date = datetime.datetime.now().astimezone(et)

    if date.weekday() > 4:
        if date.time() >= datetime.time(18,0,0):
            return str(date.date() + datetime.timedelta(days=1)) if today else str(date.date())
        else:
            return str(date.date()) if today else (str(date.date() - datetime.timedelta(days=1)))
    else:
        if date.time() >= datetime.time(22,0,0):
            return str(date.date() + datetime.timedelta(days=1)) if today else str(date.date())
        else:
            return str(date.date()) if today else (str(date.date() - datetime.timedelta(days=1)))

def should_remind() -> bool:
    """The NYT does crossword resets on 10PM EST on weekdays and 6PM EST on weekends.
    So set a reminder in the hour before the date updates.
    """
    et = pytz.timezone('US/Eastern')
    date = datetime.datetime.now().astimezone(et)

    if date.weekday() > 4:
        if date.time() >= datetime.time(17,0,0) and date.time() <= datetime.time(18,0,0):
            return True
        else:
            return False
    else:
        if date.time() >= datetime.time(21,0,0) and date.time() <= datetime.time(22,0,0):
            return True
        else:
            return False

class LeaderboardDatabaseConnection:
    def __init__(self, database_loc : str):
        self._db_con = sqlite3.connect(database_loc)
    
    def check_for_existing_score(self, score : LeaderboardEntry):
        cur = self._db_con.cursor()
        check_cmd = 'SELECT * from scores WHERE user = ? AND date = ?'
        cur.execute(check_cmd, [score.user, score.date])
        rows = cur.fetchall()
        return len(rows) > 0

    def insert_score(self, score : LeaderboardEntry):
        cur = self._db_con.cursor()
        insert_cmd = 'INSERT into scores values (?, ?, ?)'
        cur.execute(insert_cmd,[score.user, score.date, score.time])
        self._db_con.commit()

    def delete_score(self, score : LeaderboardEntry):
        cur = self._db_con.cursor()
        delete_cmd = 'DELETE from scores WHERE user = ? AND date = ?'
        cur.execute(delete_cmd,[score.user,score.date])
        self._db_con.commit()
    
    def get_scores_for_date(self, date : str):
        cur = self._db_con.cursor()
        leader_cmd = 'SELECT * FROM scores WHERE date = ? ORDER BY score'
<<<<<<< HEAD
        rows = cur.execute(leader_cmd, [date]).fetchall()
=======
        cur.execute(leader_cmd, [date])
        rows = cur.fetchall()
>>>>>>> master
        return rows

    def get_user_stats(self, user: str):
        cur = self._db_con.cursor()

        total_games = cur.execute("SELECT COUNT(*) FROM scores WHERE user = ?",[user]).fetchall()[0][0]
        avg_score = cur.execute("SELECT avg(score) FROM scores WHERE user = ?",[user]).fetchall()[0][0]
        best_score = cur.execute("SELECT min(score) FROM scores WHERE user = ?",[user]).fetchall()[0][0]
        total_wins = cur.execute("SELECT COUNT(*) FROM winners WHERE user = ?",[user]).fetchall()[0][0]
        stats_string = f"{user} stats \nTotal Games: {total_games} \nTotal Wins :trophy::  {total_wins} \nWin Percentage: {(total_wins/total_games * 100.0):.2f}% \nAverage Score :stopwatch:: {avg_score:.2f} \nBest Score :race_car: : {best_score}"

        return stats_string
    
    def build_winner_list(self, date: str) -> list:
        cur = self._db_con.cursor()
        # TODO this is gross, but it works....
        day_scores = cur.execute("SELECT * from scores WHERE date = ? ORDER BY score ", [str(date)]).fetchall()
        if not day_scores:
            return None
        winner_list = [day_scores[0][0]]
        winner_score = day_scores[0][2]
        if len(day_scores) > 1 :
            i = 1
            next_score = day_scores[i][2]
            next_winner = day_scores[i][0]
            while(winner_score == next_score):
                logging.info(f"winner score{winner_score} next score{next_score}")
                winner_list.append(next_winner)
                i += 1
                if i == len(day_scores):
                    break
                next_score = day_scores[i][2]
                next_winner = day_scores[i][0]
        return winner_list

    def update_winner_table(self, date: str):
        cur = self._db_con.cursor()
        logging.info("Running the update winner update as the date has changed")
        winner_list = self.build_winner_list(date)
        if winner_list:
            for winner in winner_list:
                logging.info(f"The winner is{winner}")
                cur.execute("INSERT INTO winners values (?, ?)", [str(winner), str(date)])
                self._db_con.commit()
    
class MiniCrosswordBot(commands.Cog):
<<<<<<< HEAD
    def __init__(self, bot : commands.Bot, ldbc : LeaderboardDatabaseConnection):
        logging.info("Spinning up the updater")
        self.date = determine_date()
        self.update_winner_table.start()
        self.remind_users.start()
        self._bot = bot
        self._db_con = ldbc
=======
    def __init__(self, bot : commands.Bot, db_path : str):
        logging.info("Spinning up the updater")
        self.date = determine_date()
        self.update_winner_table.start()
        # self.remind_users.start()
        self._bot = bot
        self._db_con = LeaderboardDatabaseConnection(db_path)
>>>>>>> master

    # Methods to help with handling commands
    @staticmethod
    def _parse_message(msg : str, command_key : str, author : str) -> Optional[LeaderboardEntry]:
        m = re.search(command_key+'\s([0-9]+):([0-9][0-9])', msg)
        if m is None:
<<<<<<< HEAD
            return None
=======
            m = re.search(command_key+'\s([0-9][0-9])', msg)
            if m is None:
                m = re.search(command_key+'\s([0-9])', msg)
                if m is None:
                   return None
            result = LeaderboardEntry()
            result.time = int(m.group(1))
            result.user = str(author)
            result.date = determine_date()
            return result
>>>>>>> master
        else:
            result = LeaderboardEntry()
            result.time = int(m.group(1)) * 60 + int(m.group(2))
            result.user = str(author)
            result.date = determine_date()
            return result

    def _build_leaderboard_string(self, date: str, rows):
        msg = f'{date} Leaderboard'

        place = 0
        last_score = None
        tie_count = 0
        for row in rows:
            if row[2] == last_score:
                tie_count += 1
            else:
                last_score = row[2]
                place += (1 + tie_count)
                tie_count = 0
            msg += f'\n{self._place_emoji_helper(place)}. {row[0]} : {self._convert_to_min_sec(row[2])}'

        return msg

    @staticmethod
    def _place_emoji_helper(place : int):
        if place == 1:
            return ":first_place:"
        elif place == 2:
            return ":second_place:"
        elif place == 3:
            return ":third_place:"
        else:
            return place

    @staticmethod
    def _convert_to_min_sec(seconds : int) -> str:
        return time.strftime("%M:%S", time.gmtime(seconds))

    def get_chan_id(self) -> id:
        for chan in self._bot.get_all_channels():
            if chan.name == "word-games":
                return chan
    # Command Logic
    def do_mini_add(self, entry: LeaderboardEntry) -> str:
        if entry is None:
            return "Error with score message format, try again, must be `m:ss`"
        else:
            if not self._db_con.check_for_existing_score(entry):
                self._db_con.insert_score(entry)
                return f"Score recorded for {entry.user} for {entry.date}"
            else:
                return f"{entry.user}, you already submitted a score today"


    def do_mini_correct(self, entry : LeaderboardEntry) -> str:
        if entry is None:
            return  "Error with score message format, try again, must be `m:ss`"
        else:
            if not self._db_con.check_for_existing_score(entry):
                return f"You don't have a score to correct today {entry.user}"
            else:
                self._db_con.delete_score(entry)
                self._db_con.insert_score(entry)
                return f"Score corrected for {entry.user} for {entry.date}"

    # Command entry points
    @commands.command(name='mini-leader', help="Responds with today's leaderboard")
    async def handle_leaderboard(self, ctx):
        date = determine_date()
        rows = self._db_con.get_scores_for_date(date)
        msg = self._build_leaderboard_string(date, rows)
        await ctx.send(msg)

    @commands.command(name='mini-yesterday', help="Responds with yesterday's leaderboard")
    async def handle_yesterday_leaderboard(self, ctx):          
        date = determine_date(False)
        rows = self._db_con.get_scores_for_date(date)
        msg = self._build_leaderboard_string(date, rows)
        await ctx.send(msg)

    @commands.command(name='mini-score', help="Allows you to submit your score for today in format m:ss")
    async def handle_mini_score(self, ctx):
        res = self._parse_message(ctx.message.content, '!mini-score', ctx.message.author)
        await ctx.send(self.do_mini_add(res))
    
    @commands.command(name='mini-correct', help="Correct your score if you made a mistake submitting today")
    async def handle_mini_correct(self, ctx):
        res = self._parse_message(ctx.message.content, '!mini-correct', ctx.message.author)
        await ctx.send(self.do_mini_correct(res))

    @commands.command(name='mini-delete', help='Delete your submitted score')
    async def handle_mini_delete(self, ctx):
        score = LeaderboardEntry(user=ctx.message.author, date=determine_date())
        self._db_con.delete_score(score)
        await ctx.send(f"Score deleted for {score.user} for {score.date}")

    @commands.command(name='mini-stats', help='Get your mini stats')
    async def handle_mini_stats(self, ctx):
        stats_string = self._db_con.get_user_stats(str(ctx.message.author))
        await ctx.send(stats_string)

    @commands.command(name='mini-join-reminder', help='Join the mini crossword reminder group')
    async def handle_mini_join(self, ctx):
        guild = self._bot.get_guild(ctx.guild.id)
        role = None
        for role_it in guild.roles:
            if str(role_it) == ROLE_NAME:
                role = role_it
        if not role:
            logging.error("The crossword role does not exist can't add user")
            await ctx.send("Error joining crossword reminder group, might not exist, contact admin")
        tasks = [ctx.message.author.add_roles(role), ctx.send(f"Adding {ctx.message.author} to the mini crossword reminder group")]
        await asyncio.wait(tasks)

    @commands.command(name='mini-leave-reminder', help='Leave the mini crossword reminder group')
    async def handle_mini_leave(self, ctx):
        guild = self._bot.get_guild(ctx.guild.id)
        role = None
        for role_it in guild.roles:
            if str(role_it) == ROLE_NAME:
                role = role_it
        if not role:
            logging.error("The crossword role does not exist can't add user")
            await ctx.send("Error deleting crossword reminder group, might not exist, contact admin")
        tasks = [ctx.message.author.remove_roles(role), ctx.send(f"Removing {ctx.message.author} from the mini crossword reminder group")]
        await asyncio.wait(tasks)

    # Tasks and task setup
    @tasks.loop(hours=1.0)
    async def update_winner_table(self):
        # check that 
        logging.info("Checking if the winner table needs to be updated")
        cur_date = determine_date()
        if cur_date != self.date:
            self._db_con.update_winner_table(self.date)
            self.date = cur_date
        return

    def reminder_task(self) -> Optional[str]:
        if should_remind():
            # TODO make this not one guild specific...
            guild = None
            for guild_id in bot.guilds:
                if str(guild_id) == GUILD_NAME:
                    guild = guild_id
                    break
            role_id = None
            for role in guild.roles:
                if str(role) == ROLE_NAME:
                    role_id = role
                    break
            if role_id:
                return f"Don't forget to submit your crossword scores <@&{role_id.id}>"
        return None

    @tasks.loop(hours=1.0)
    async def remind_users(self):
        msg = self.reminder_task()
        if msg:
            chan = self.get_chan_id()
            await chan.send(msg)
    
    @update_winner_table.before_loop
    async def before_start(self):
        await self._bot.wait_until_ready()

    @remind_users.before_loop
    async def before_start(self):
<<<<<<< HEAD
        await self._bot.wait_until_ready()
=======
        await bot.wait_until_ready()
>>>>>>> master

# Setup Things
async def create_crossword_role(guild : discord.guild):
    logging.info("Attempting to create a guild")
    print(guild)
    for role in guild.roles:
        if str(role) == ROLE_NAME:
            return
    await guild.create_role(name=ROLE_NAME)

async def create_crossword_role_all_guilds():
    logging.info("create all the roles")
<<<<<<< HEAD
    tasks = [create_crossword_role(guild) for guild in g_bot.guilds]
    await asyncio.wait(tasks)

@g_bot.event
async def on_ready():
    tasks = [create_crossword_role_all_guilds(), g_bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="to !help"))]
=======
    tasks = [create_crossword_role(guild) for guild in bot.guilds]
    await asyncio.wait(tasks)

@bot.event
async def on_ready():
    tasks = [create_crossword_role_all_guilds(), bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="to !help"))]
>>>>>>> master
    await asyncio.wait(tasks)


def main():
    logging.basicConfig(filename='crossword_bot.log', level=logging.INFO)
    logging.info('Starting the crossword bot')
    # daily_updater = DailyUpdater()
<<<<<<< HEAD
    ldbc = LeaderboardDatabaseConnection('scores.db')
    g_bot.add_cog(MiniCrosswordBot(g_bot, ldbc))
    g_bot.run(TOKEN)
    
if __name__ == '__main__':
    main() 
=======
    bot.add_cog(MiniCrosswordBot(bot, 'scores.db'))
    bot.run(TOKEN)
    
if __name__ == '__main__':
    main() 
>>>>>>> master
