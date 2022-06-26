import pytest
import sqlite3
from unittest.mock import MagicMock, Mock, patch 
from mini_crossword_bot.bot import LeaderboardDatabaseConnection
from mini_crossword_bot.bot import LeaderboardEntry

#Note: Mocking the database connection, so I only have to test logic
@pytest.mark.parametrize("return_vals,expected",[(['1'],True),([], False)])
def test_check_for_existing_score(return_vals, expected):
    with patch('mini_crossword_bot.bot.sqlite3') as mocksql:
        # Setup 
        mocksql.connect().return_value = None
        mocksql.connect().cursor().return_value = None
        mocksql.connect().execute().return_value = None
        mocksql.connect().cursor().fetchall.return_value = return_vals

        test_con = LeaderboardDatabaseConnection('test.db')
        assert expected == test_con.check_for_existing_score(LeaderboardEntry())

@pytest.mark.parametrize("return_vals,expected",
    [
    ([['Dan','date',0]],['Dan']),
    ([['Dan','date',0],['Bobby','date',1]],['Dan']),
    ([], None),
    ([['Dan','date',1],['Bobby','date',1]],['Dan','Bobby']),
    ([['Dan','date',1],['Bobby','date',1],['Brigid','date',1]],['Dan','Bobby','Brigid'])
    ])
def test_build_winner_list(return_vals, expected):
    with patch('mini_crossword_bot.bot.sqlite3') as mocksql:
        # Setup 
        mocksql.connect().return_value = None
        mocksql.connect().cursor().return_value = None
        mocksql.connect().execute().return_value = None
        mocksql.connect().cursor().execute().fetchall.return_value = return_vals

        test_con = LeaderboardDatabaseConnection('test.db')
        assert expected == test_con.build_winner_list('test')