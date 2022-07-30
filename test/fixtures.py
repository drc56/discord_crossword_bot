import pytest
import sqlite3
from unittest.mock import MagicMock, Mock, AsyncMock, patch
from mini_crossword_bot.bot import LeaderboardDatabaseConnection, MiniCrosswordBot 
from discord.ext import commands, tasks

#Note: Mocking the database connection, so I only have to test logic
@pytest.fixture
def mocksql_none_fixture():
    with patch('mini_crossword_bot.bot.sqlite3') as mocksql:
        mocksql.connect().return_value = None
        mocksql.connect().cursor().return_value = None
        mocksql.connect().execute().return_value = None
        yield mocksql

class MockBot:
    wait_until_ready = AsyncMock(return_value=(True))

@pytest.fixture
def discord_bot_mocker(): 
    bot = MockBot()
    yield bot

class LeaderboardDatabaseConnectionMock(LeaderboardDatabaseConnection):
    def __init__(self, database_loc: str, mock_results):
        self._mock_results = mock_results
        pass
    
    def get_scores_for_date(self, date: str):
        print(self._mock_results)
        return self._mock_results