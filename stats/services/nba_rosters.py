import mysql.connector
import requests
from bs4 import BeautifulSoup
import settings
import time

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database='nba')
cursor = cnx.cursor(buffered=True)

add_player = ("INSERT INTO players "
            "(stats_id, status, first_name, last_name, height, weight, position, jersey_number, experience, college, "
              "birth_place, birthdate, updated, team_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

query = ("SELECT * FROM teams")
cursor.execute(query)

for id in cursor.fetchall():
    team_id = id[0]
    print(team_id)
    print(id[1])
    print(' =====  ')
    stats_id = id[1]
    time.sleep(5)
    r = requests.get(
        "https://api.sportradar.us/nba-t3/teams/" + stats_id + "/profile.xml?api_key=u87kvnfukh8392duutyvc3en")

    soup = BeautifulSoup(r.content, "html.parser")
    # soup = BeautifulSoup(open("../../xml/nba_team_roster.xml"), "html.parser")

    players = soup.findAll('player')

    for p in players:
        print(p.get('id'))

        data_player = (
            p.get('id'), p.get('status'), p.get('first_name'), p.get('last_name'), p.get('height'), p.get('weight'),
            p.get('position'), p.get('jersey_number'), p.get('experience'), p.get('college'), p.get('birth_place'),
            p.get('birthdate'), p.get('updated'), team_id)

        cursor.execute(add_player, data_player)
        cnx.commit()


