import pytest
from fixtures import discord_bot_mocker, LeaderboardDatabaseConnectionMock
from mini_crossword_bot.bot import MiniCrosswordBot, determine_date



class ContextHelper:
    def __init__(self, expected_result : str):
        self._expected_result = expected_result
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
    ]
)
async def test_build_winner_list(discord_bot_mocker, return_vals, expected):
    ldbc = LeaderboardDatabaseConnectionMock('test.db',return_vals)
    mc_bot = MiniCrosswordBot(discord_bot_mocker, ldbc)
    await mc_bot.handle_leaderboard(mc_bot, ContextHelper(expected))

