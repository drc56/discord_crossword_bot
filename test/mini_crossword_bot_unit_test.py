from dataclasses import dataclass
import pytest
from fixtures import discord_bot_mocker, LeaderboardDatabaseConnectionMock, LeaderboardDatabaseConnectionExistsMock
from mini_crossword_bot.bot import MiniCrosswordBot, determine_date

@dataclass
class MessageHelper:
    content : str
    author : str

class ContextHelper:
    def __init__(self, expected_result : str, message : str="", author : str=""):
        self._expected_result = expected_result
        self.message = MessageHelper(message, author)
    async def send(self, msg : str):
        print(msg)
        assert(msg == self._expected_result)

@pytest.mark.asyncio
@pytest.mark.parametrize("return_vals,expected",
    [
    ([['Dan',f'{determine_date()}',1]],f'{determine_date()} Leaderboard\n:first_place:. Dan : 00:01'),
    ([['Dan',f'{determine_date()}',1],['Bobby',f'{determine_date()}',2]],
    f'{determine_date()} Leaderboard\n:first_place:. Dan : 00:01\n:second_place:. Bobby : 00:02'),
    ([['Dan',f'{determine_date()}',1],['Bobby',f'{determine_date()}',2],['Dave',f'{determine_date()}',3]],
    f'{determine_date()} Leaderboard\n:first_place:. Dan : 00:01\n:second_place:. Bobby : 00:02\n:third_place:. Dave : 00:03'),
    ([['Dan',f'{determine_date()}',1],['Bobby',f'{determine_date()}',2],['Dave',f'{determine_date()}',3],['Brigid',f'{determine_date()}',4]],
    f'{determine_date()} Leaderboard\n:first_place:. Dan : 00:01\n:second_place:. Bobby : 00:02\n:third_place:. Dave : 00:03\n4. Brigid : 00:04'),
    ([['Dan',f'{determine_date()}',1],['Bobby',f'{determine_date()}',1],['Dave',f'{determine_date()}',3]],
    f'{determine_date()} Leaderboard\n:first_place:. Dan : 00:01\n:first_place:. Bobby : 00:01\n:third_place:. Dave : 00:03'), 
    ]
)
async def test_build_winner_list(discord_bot_mocker, return_vals, expected):
    ldbc = LeaderboardDatabaseConnectionMock('test.db',return_vals)
    mc_bot = MiniCrosswordBot(discord_bot_mocker, ldbc)
    await mc_bot.handle_leaderboard(mc_bot, ContextHelper(expected))

@pytest.mark.asyncio
@pytest.mark.parametrize("msg,author,expected", 
    [
      ('!mini-score 0:48','dan',f'Score recorded for dan for {determine_date()}'),  
      ('!mini-score 1:48','dan',f'Score recorded for dan for {determine_date()}'),  
      ('!mini-score 0:148','dan',f'Score recorded for dan for {determine_date()}'), 
      ('!mini-score 48','dan',f'Score recorded for dan for {determine_date()}'), 
      ('!mini-score 4','dan',f'Score recorded for dan for {determine_date()}'), 
      ('!mini-score XYZ','dan',f'Error with score message format, try again, must be `m:ss`'),  
      ('!mini-score 2m42s','dan',f'Error with score message format, try again, must be `m:ss`'),  
    ]
)
async def test_mini_score(discord_bot_mocker, msg, author, expected):
    ldbc = LeaderboardDatabaseConnectionMock('test.db',None)
    mc_bot = MiniCrosswordBot(discord_bot_mocker, ldbc)
    await mc_bot.handle_mini_score(mc_bot, ContextHelper(expected, msg, author))

@pytest.mark.asyncio
@pytest.mark.parametrize("msg,author,expected", 
    [
      ('!mini-score 0:48','dan',f'dan, you already submitted a score today'),  
    ]
)
async def test_mini_score_exists(discord_bot_mocker, msg, author, expected):
    ldbc = LeaderboardDatabaseConnectionExistsMock('test.db',None)
    mc_bot = MiniCrosswordBot(discord_bot_mocker, ldbc)
    await mc_bot.handle_mini_score(mc_bot, ContextHelper(expected, msg, author))

@pytest.mark.asyncio
@pytest.mark.parametrize("msg,author,expected", 
    [
      ('!mini-correct 0:48','dan',f'Score corrected for dan for {determine_date()}'),  
      ('!mini-correct 1:48','dan',f'Score corrected for dan for {determine_date()}'),  
      ('!mini-correct 0:148','dan',f'Score corrected for dan for {determine_date()}'), 
      ('!mini-correct 48','dan',f'Score corrected for dan for {determine_date()}'), 
      ('!mini-correct 4','dan',f'Score corrected for dan for {determine_date()}'), 
      ('!mini-correct XYZ','dan',f'Error with score message format, try again, must be `m:ss`'),  
      ('!mini-correct 2m42s','dan',f'Error with score message format, try again, must be `m:ss`'),  
    ]
)
async def test_mini_correct(discord_bot_mocker, msg, author, expected):
    ldbc = LeaderboardDatabaseConnectionExistsMock('test.db',None)
    mc_bot = MiniCrosswordBot(discord_bot_mocker, ldbc)
    await mc_bot.handle_mini_correct(mc_bot, ContextHelper(expected, msg, author))
