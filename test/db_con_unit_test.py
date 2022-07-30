import pytest
from fixtures import mocksql_none_fixture
from mini_crossword_bot.bot import LeaderboardDatabaseConnection
from mini_crossword_bot.bot import LeaderboardEntry

@pytest.mark.parametrize("return_vals,expected",[(['1'],True),([], False)])
def test_check_for_existing_score(mocksql_none_fixture, return_vals, expected):
    mocksql_none_fixture.connect().cursor().fetchall.return_value = return_vals
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
def test_build_winner_list(mocksql_none_fixture, return_vals, expected):
    mocksql_none_fixture.connect().cursor().execute().fetchall.return_value = return_vals
    test_con = LeaderboardDatabaseConnection('test.db')
    assert expected == test_con.build_winner_list('test')