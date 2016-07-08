import json, requests
import mysql.connector
from datetime import datetime, date, time

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mlb')
cursor = cnx.cursor()

API_KEY = "patymcysmye3a82xp5kf5ba4"
VERSION = "t5"
YEAR = "2016"

r = requests.get('https://api.sportradar.us/mlb-' + VERSION + '/games/' + YEAR + '/reg/schedule.json?api_key=' + API_KEY)

data = r.text
json_data = json.loads(data)
add_game = ("INSERT INTO games "
                "(day_night, scheduled, home_team, away_team, venue, stats_id) "
                "VALUES (%s, %s, %s, %s, %s, %s)")
games = json_data["league"]["season"]["games"]
for game in games:

    schedule = game["scheduled"][:-6]
    dt = datetime.strptime(schedule, "%Y-%m-%dT%H:%M:%S")

    query = ("SELECT id FROM teams "
             "WHERE stats_id = %(home_id)s")
    cursor.execute(query, { 'home_id': game["home_team"] })

    for id in cursor:
        home_id = id[0]

    query = ("SELECT id FROM teams "
             "WHERE stats_id = %(away_id)s")
    cursor.execute(query, {'away_id': game["away_team"]})

    for id in cursor:
        away_id = id[0]

    query = ("SELECT id FROM venues "
             "WHERE stats_id = %(venue_id)s")
    cursor.execute(query, {'venue_id': game["venue"]["id"]})

    for id in cursor:
        venue_id = id[0]

    data_game = (game["day_night"], game["scheduled"], home_id, away_id, venue_id, game["id"])
    # Insert Roster
    cursor.execute(add_game, data_game)
    cnx.commit()

cursor.close()
cnx.close()