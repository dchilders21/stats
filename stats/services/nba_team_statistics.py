import mysql.connector
import requests
from bs4 import BeautifulSoup
import settings
import time

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database='nba')
cursor = cnx.cursor(buffered=True)

add_stats = ("INSERT INTO game_stats "
            "(game_id, team_id, is_home, player_id, min, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, DREB, AST, STL, BLK, turnovers, "
             "PF, plus_minus, PTS) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

add_totals = ("INSERT INTO team_totals "
             "(game_id, team_id, is_home, FGM, FGA, 3PM, 3PA, FTM, FTA, OREB, DREB, AST, STL, BLK, "
              "turnovers, PF, 1st_qtr, 2nd_qtr, 3rd_qtr, 4th_qtr, total_pts, fast_break_points, "
              "points_in_paint, points_off_turnovers, second_chance_points) "
             "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

query = ("SELECT * FROM games WHERE status = 'closed'")
cursor.execute(query)

''' Loop through Games '''
for row in cursor.fetchall():
    game_id = row[1]

    print(game_id)
    print(' =====  ')
    time.sleep(3)
    r = requests.get(
        "https://api.sportradar.us/nba-t3/games/" + game_id + "/summary.xml?api_key=u87kvnfukh8392duutyvc3en")

    soup = BeautifulSoup(r.content, "html.parser")
    # soup = BeautifulSoup(open("../../xml/nba_game_summary_example.xml"), "html.parser")

    game = soup.find('game')
    home_team = game.get('home_team')

    teams = soup.findAll('team')

    """ Loop through both teams"""
    for t in teams:

        query = ("SELECT id FROM teams "
                 "WHERE stats_id = %(team_id)s")
        cursor.execute(query, {'team_id': t.get('id')})

        for id in cursor:
            team_id = id[0]

        if t.get('id') == home_team:
            is_home = 1
        else:
            is_home = 0

        ts = t.find('statistics')
        quarters = t.findAll('quarter')

        data_totals = (
            row[0], team_id, is_home,
            ts.get('field_goals_made'), ts.get('field_goals_att'), ts.get('three_points_made'), ts.get('three_points_att'),
            ts.get('free_throws_made'), ts.get('free_throws_att'),
            ts.get('offensive_rebounds'), ts.get('defensive_rebounds'), ts.get('assists'), ts.get('steals'),
            ts.get('blocks'), ts.get('turnovers'), ts.get('personal_fouls'),
            quarters[0].get('points'), quarters[1].get('points'), quarters[2].get('points'), quarters[3].get('points'),
            ts.get('points'), ts.get('fast_break_pts'), ts.get('paint_pts'),
            ts.get('points_off_turnovers'),  ts.get('second_chance_pts'))

        cursor.execute(add_totals, data_totals)
        cnx.commit()

        """ Loop through the players """
        players = soup.findAll('player')

        for p in players:

            query = ("SELECT id FROM players "
                     "WHERE stats_id = %(player_id)s")
            cursor.execute(query, {'player_id': p.get('id')})

            for id in cursor:
                player_id = id[0]

            s = p.find('statistics')

            data_stats = (
                row[0], team_id, is_home, player_id, s.get('minutes'),
                s.get('field_goals_made'), s.get('field_goals_att'), s.get('three_points_made'), s.get('three_points_att'),
                s.get('free_throws_made'), s.get('free_throws_att'),
                s.get('offensive_rebounds'), s.get('defensive_rebounds'), s.get('assists'), s.get('steals'),
                s.get('blocks'), s.get('turnovers'), s.get('personal_fouls'),
                s.get('pls_min'), s.get('points'))

            cursor.execute(add_stats, data_stats)
            cnx.commit()


