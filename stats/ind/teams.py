import mysql.connector
from bs4 import BeautifulSoup
import settings

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database='nba')
cursor = cnx.cursor()

add_team = ("INSERT INTO teams "
            "(stats_id, name, market, division_name, division_id, division_alias, "
            "conference_name, conference_id, conference_alias) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")


soup = BeautifulSoup(open("../../xml/nba_2016_teams.xml"), "html.parser")

teams = soup.findAll('team')

for t in teams:
    print(t.parent.parent.get('id'))
    print(t.parent.parent.get('name'))
    print(t.parent.parent.get('alias'))
    print(t.parent.get('id'))
    print(t.parent.get('name'))
    print(t.parent.get('alias'))
    print(t.get('id'))
    print(t.get('name'))
    print(t.get('market'))
    print(' ==== ')

    data_team = (
        t.get('id'), t.get('name'), t.get('market'), t.parent.get('name'), t.parent.get('id'),
        t.parent.get('alias'), t.parent.parent.get('name'), t.parent.parent.get('id'), t.parent.parent.get('alias'))
    cursor.execute(add_team, data_team)
    cnx.commit()


