import json, requests
import mysql.connector
import time

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mlb')
cursor = cnx.cursor(buffered=True)

API_KEY = "patymcysmye3a82xp5kf5ba4"
VERSION = "t5"
YEAR = "2016"

#query = ("SELECT id, home_team, away_team, stats_id FROM games")
query = ("SELECT id, home_team, away_team, stats_id FROM games WHERE id > 10418 LIMIT 0, 1200")

cursor.execute(query)

games = cursor.fetchall()

for id, home_team, away_team, stats_id in games:
    time.sleep(2)
    url = 'http://api.sportradar.us/mlb-t5/games/{}/pbp.json?api_key=patymcysmye3a82xp5kf5ba4'.format(stats_id)
    print(url)
    r = requests.get(url)
    data = r.text
    json_data = json.loads(data)
    if json_data["game"]["status"] == "closed":
        innings = json_data["game"]["innings"]
        for inning in innings:
            if inning["number"] > 0:
                add_inning = ("INSERT INTO innings "
                              "(game_id, home_id, away_id, number, sequence, home_runs, away_runs) "
                              "VALUES (%s, %s, %s, %s, %s, %s, %s)")
                data_inning = (id, home_team, away_team, inning["number"], inning["sequence"],
                               inning["scoring"]["home"]["runs"], inning["scoring"]["away"]["runs"])
                cursor.execute(add_inning, data_inning)
                cnx.commit()

cursor.close()
cnx.close()