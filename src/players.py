import mysql.connector
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date, time
import time


cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
API_KEY = "b99x88uxzrfbvm9kxtfmabth"
VERSION = "t2"

cursor = cnx.cursor(buffered=True)
query = ("SELECT id, stats_id FROM teams")
cursor.execute(query)

teams = cursor.fetchall()

for id, stats_id in teams:
    print(id)
    r = requests.get('http://api.sportradar.us/soccer-' + VERSION + '/na/teams/' + stats_id + '/profile.xml?api_key=' + API_KEY)
    soup = BeautifulSoup(r.content, "html.parser")
    players = soup.find_all('player')
    print(players)
    for player in players:
        birthdate = player['birthdate']
        if (birthdate != ""):
            dt = datetime.strptime(birthdate, "%Y-%m-%d")

        add_player = ("INSERT INTO players "
                      "(first_name, last_name, country_code, country, preferred_foot, birthdate, height_in, weight_lb, height_cm, weight_kg, jersey_number, position, stats_id, team_id) "
                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        data_player = (
            player['first_name'], player['last_name'], player['country_code'], player['country'], player['preferred_foot'],
            birthdate, player['height_in'], player['weight_lb'], player['height_cm'], player['weight_kg'], player['jersey_number'], player['position'], player["id"], id)

        cursor.execute(add_player, data_player)
        cnx.commit()

cursor.close()
cnx.close()



