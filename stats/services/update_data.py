#!/anaconda3/envs/stats/bin/python3 python

import mysql.connector
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

''' Finds the most current round '''
leagues = ['primera_division', 'ligue_1', 'epl', 'bundesliga']

cnx = mysql.connector.connect(user='admin', password='1Qaz@wsx',
                              host='0.0.0.0',
                              database='mls')
cursor = cnx.cursor(buffered=True)

rounds = []

for l in leagues:
    matches_table = 'matches_' + l
    q = "SELECT MIN(round_number) as round FROM " + matches_table + " WHERE status = 'scheduled'"

    matches = pd.read_sql(q, cnx)
    rounds.append(matches.iloc[0]['round'])

print(rounds)

API_KEY = "au5hqx7j6uag8zrryy5ubh6b"
VERSION = "t2"

for r in range(len(rounds)):
    table = 'matches_' + leagues[r]

    query = ("SELECT id, stats_id FROM " + table + " WHERE round_number = %(round)s AND status = 'scheduled'")

    cursor.execute(query, {'round': float(rounds[r])})

    coverage_table = 'match_coverage_' + leagues[r]
    home_manager_table = str('home_manager_' + leagues[r])
    away_manager_table = str('away_manager_' + leagues[r])
    home_team_coverage_table = 'home_team_coverage_' + leagues[r]
    away_team_coverage_table = 'away_team_coverage_' + leagues[r]

    matches = cursor.fetchall()
    for id, stats_id in matches:

        # Checking to see if the match (match_id) has already been added to match_coverage
        query = ("SELECT id FROM " + coverage_table + " "
                 "WHERE match_id = %(match_id)s")
        cursor.execute(query, {'match_id': id})

        if (cursor.rowcount != 0):
            print("Match ID already Exists in DB")
        else:
            time.sleep(2)
            url = "http://api.sportradar.us/soccer-" + VERSION + "/eu/matches/" + stats_id + "/summary.xml?api_key=" + API_KEY
            print(id)
            print(url)
            r = requests.get(url)

            soup = BeautifulSoup(r.content, "html.parser")
            #soup = BeautifulSoup(open("./xml/game_summary.xml"), "html.parser")
            #print(r.content)

            # Match_Coverage
            add_coverage = ("INSERT INTO " + coverage_table + " "
                        "(lineups, tactical_lineups, corner_facts, extended_facts, deep_facts, statistics, referee_id, match_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")

            match = soup.find('match')
            coverage = soup.find('coverage')
            match_id = id

            referee = soup.find('referee')

            if referee is None:
                referee = ""
            else:
                referee_id = referee.get("id")

            data_coverage = (
                coverage.get("lineups"), coverage.get("tactical_lineups"), coverage.get("corner_facts"), coverage.get("extended_facts"), coverage.get("deep_facts"),
                coverage.get("statistics"), referee_id, id)

            cursor.execute(add_coverage, data_coverage)
            cnx.commit()

            # Home/Away Managers
            home = soup.find('home')
            away = soup.find('away')

            add_home_manager = ("INSERT INTO " + home_manager_table + " "
                            "(stats_id, match_id) "
                            "VALUES (%s, %s)")

            add_away_manager = ("INSERT INTO " + away_manager_table + " "
                                "(stats_id, match_id) "
                                "VALUES (%s, %s)")

            home_manager = home.find('manager')
            away_manager = away.find('manager')

            if home_manager is not None and away_manager is not None:
                data_home_manager = (
                    home.find('manager').get("id"), id)

                data_away_manager = (
                    away.find('manager').get("id"), id)

                cursor.execute(add_away_manager, data_away_manager)

                cursor.execute(add_home_manager, data_home_manager)

                cnx.commit()

            # Home/Away Coverage
            home_halves = home.find_all("half")
            home_stats = home.find("statistics")
            away_halves = away.find_all("half")
            away_stats = away.find("statistics")

            home_winner = 0
            away_winner = 0

            if home["winner"] == "true":
                home_winner = 1
            elif home["winner"] == "draw":
                home_winner = 2

            if away["winner"] == "true":
                away_winner = 1
            elif away["winner"] == "draw":
                away_winner = 2

            add_home_team_coverage = ("INSERT INTO " + home_team_coverage_table + " "
                            "(stats_id, formation, score, regular_score, penalty_score, winner, first_half_score, second_half_score, attacks, ball_safe, "
                                      "corner_kicks, dangerous_attacks, fouls, free_kicks, goal_attempts, goal_kicks, offsides, saves, substitutions, throw_ins,"
                                      " yellow_card, shots_on_target, shots_off_target, shots_total, possessions, match_id) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

            data_home_team_coverage = (
                home["id"], home["formation"], home["score"], home["regular_score"], home["penalty_score"], home_winner,
                home_halves[0]["points"], home_halves[1]["points"], home_stats.get("attacks"), home_stats.get("ball_safe"), home_stats.get("corner_kicks"), home_stats.get("dangerous_attacks"),
                home_stats.get("fouls"), home_stats.get("free_kicks"), home_stats.get("goal_attempts"), home_stats.get("goal_kicks"), home_stats.get("offsides"),
                home_stats.get("saves"), home_stats.get("substitutions"), home_stats.get("throw_ins"), home_stats.get("yellow_card"), home_stats.get("shots_on_target"),
                home_stats.get("shots_off_target"), home_stats.get("shots_total"), home_stats.get("possessions"), id)

            add_away_team_coverage = ("INSERT INTO " + away_team_coverage_table + " "
                                      "(stats_id, formation, score, regular_score, penalty_score, winner, first_half_score, second_half_score, attacks, ball_safe, "
                                      "corner_kicks, dangerous_attacks, fouls, free_kicks, goal_attempts, goal_kicks, offsides, saves, substitutions, throw_ins,"
                                      " yellow_card, shots_on_target, shots_off_target, shots_total, possessions, match_id) "
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

            data_away_team_coverage = (
                away["id"], away["formation"], away["score"], away["regular_score"], away["penalty_score"], away_winner,
                away_halves[0]["points"], away_halves[1]["points"], away_stats.get("attacks"), away_stats.get("ball_safe"),
                away_stats.get("corner_kicks"), away_stats.get("dangerous_attacks"),
                away_stats.get("fouls"), away_stats.get("free_kicks"), away_stats.get("goal_attempts"), away_stats.get("goal_kicks"),
                away_stats.get("offsides"),
                away_stats.get("saves"), away_stats.get("substitutions"), away_stats.get("throw_ins"), away_stats.get("yellow_card"),
                away_stats.get("shots_on_target"),
                away_stats.get("shots_off_target"), away_stats.get("shots_total"), away_stats.get("possessions"), id)

            cursor.execute(add_home_team_coverage, data_home_team_coverage)
            cursor.execute(add_away_team_coverage, data_away_team_coverage)

            cnx.commit()

            query = ("UPDATE " + table + " SET status = 'closed' WHERE stats_id = %(stats_id)s")

            cursor.execute(query, {'stats_id': stats_id})

            cnx.commit()






