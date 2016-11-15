import mysql.connector
from bs4 import BeautifulSoup
import settings

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database='nba')
cursor = cnx.cursor()

add_game = ("INSERT INTO games "
            "(stats_id, status, scheduled, home_id, away_id, venue_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)")


soup = BeautifulSoup(open("../../xml/nba_2016_schedule.xml"), "html.parser")

games = soup.findAll('game')

for g in games:

    home_team = g.find('home')
    away_team = g.find('away')
    venue = g.find('venue')

    query = ("SELECT id FROM teams "
             "WHERE stats_id = %(home_id)s")
    cursor.execute(query, {'home_id': home_team.get('id')})

    for id in cursor:
        home_id = id[0]

    query = ("SELECT id FROM teams "
                 "WHERE stats_id = %(away_id)s")
    cursor.execute(query, {'away_id': away_team.get('id')})

    for id in cursor:
        away_id = id[0]

    print(' ===== ')
    print(home_id)
    print(away_id)


    data_game = (
        g.get('id'), g.get('status'), g.get('scheduled'), home_id, away_id, venue.get('id'))
    cursor.execute(add_game, data_game)
    cnx.commit()


