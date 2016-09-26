import mysql.connector
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, date, time
import time

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor()

# NA key - b99x88uxzrfbvm9kxtfmabth
# EU key - au5hqx7j6uag8zrryy5ubh6b
API_KEY = "b99x88uxzrfbvm9kxtfmabth"
VERSION = "t2"

cursor = cnx.cursor(buffered=True)
query = ("SELECT id, stats_id FROM matches WHERE stats_id='ac24cb5c-77f2-4abb-905f-651c1d8550ce'")
# query = ("SELECT id, stats_id FROM matches WHERE status='closed'")
cursor.execute(query)

matches = cursor.fetchall()

for id, stats_id in matches:

    print(id)
    #Checking to see if the match (match_id) has already been added to match_coverage
    query = ("SELECT id FROM match_coverage_mls "
             "WHERE match_id = %(match_id)s")
    cursor.execute(query, {'match_id': id})

    if (cursor.rowcount != 0):
        print("Match ID already Exists in DB")
    else:
        time.sleep(2)
        url = "http://api.sportradar.us/soccer-" + VERSION + "/na/matches/" + stats_id + "/summary.xml?api_key=" + API_KEY
        print(url)
        r = requests.get(url)

        soup = BeautifulSoup(r.content, "html.parser")
        #soup = BeautifulSoup(open("./xml/game_summary.xml"), "html.parser")

        ### Match_Coverage
        add_coverage = ("INSERT INTO match_coverage_mls "
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

        ### Home/Away Managers

        home = soup.find('home')
        away = soup.find('away')

        add_home_manager = ("INSERT INTO home_manager_mls "
                        "(stats_id, match_id) "
                        "VALUES (%s, %s)")

        add_away_manager = ("INSERT INTO away_manager_mls "
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

        ### Home/Away Coverage

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



        add_home_team_coverage = ("INSERT INTO home_team_coverage_mls "
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

        add_away_team_coverage = ("INSERT INTO away_team_coverage_mls "
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

        ### Home/Away Players


        """home_players = home.find_all("player")
        away_players = away.find_all("player")

        add_home_player= ("INSERT INTO home_players "
                        "(stats_id, position, started, jersey_number, tactical_position, tactical_order, goal, goal_assist, own_goal, yellow_card, yellow_red_card, "
                          "red_card, substitution_out, substitution_in, match_id) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        add_away_player = ("INSERT INTO away_players "
                           "(stats_id, position, started, jersey_number, tactical_position, tactical_order, goal, goal_assist, own_goal, yellow_card, yellow_red_card, "
                           "red_card, substitution_out, substitution_in, match_id) "
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")


        for player in home_players:

            if (player.has_attr("tactical_position")):
                tactical_position = (player["tactical_position"])
            else:
                tactical_position = -1

            if (player.has_attr("tactical_order")):
                tactical_order = (player["tactical_order"])
            else:
                tactical_order = -1

            home_started = int(player["started"] == 'true')

            data_home_player = (
                player["id"], player["position"], home_started, player["jersey_number"], tactical_position, tactical_order,
                player.find('statistics')["goal"], player.find('statistics')["goal_assist"], player.find('statistics')["own_goal"],
                player.find('statistics')["yellow_card"], player.find('statistics')["yellow_red_card"], player.find('statistics')["red_card"],
                player.find('statistics')["substitution_out"], player.find('statistics')["substitution_in"], id)

            cursor.execute(add_home_player, data_home_player)

        for player in away_players:

            if (player.has_attr("tactical_position")):
                tactical_position = (player["tactical_position"])
            else:
                tactical_position = -1

            if (player.has_attr("tactical_order")):
                tactical_order = (player["tactical_order"])
            else:
                tactical_order = -1

            away_started = int(player["started"] == 'true')

            data_away_player = (
                player["id"], player["position"], away_started, player["jersey_number"], tactical_position, tactical_order,
                player.find('statistics')["goal"], player.find('statistics')["goal_assist"], player.find('statistics')["own_goal"],
                player.find('statistics')["yellow_card"], player.find('statistics')["yellow_red_card"], player.find('statistics')["red_card"],
                player.find('statistics')["substitution_out"], player.find('statistics')["substitution_in"], id)

            #print(data_away_player)

            cursor.execute(add_away_player, data_away_player)

        cnx.commit()"""

        ### Match Facts

        """facts = soup.find_all('fact')

        for fact in facts:
            query = "INSERT INTO match_facts ("
            query_vars = ""
            results = []

            description = fact.find("description")


            for key in fact.attrs:
                if (key == "id"):
                    query += "stats_id"
                else:
                    query += key

                query += ', '


                if (key == "updated_time") or (key == "time"):
                    results.append(fact.attrs[key][:-1])
                elif (key == "header") or (key == "draw") or (key == "owngoal") or (key == "penalty") or (key == "scratch"):
                    results.append(str(int(fact.attrs[key] == 'true')))
                else:
                    results.append(str(fact.attrs[key]))

                query_vars += "%s"
                query_vars += ', '

            query += "description, match_id) VALUES ("
            query_vars += "%s, %s)"

            if description is None:
                results.append(" ")
            else:
                results.append(description.get_text())

            results.append(id)

            query += query_vars

            add_facts = (query)
            data_facts = (results)
            cursor.execute(add_facts, data_facts)

        cnx.commit()"""






