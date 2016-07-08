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
    time.sleep(2)
    r = requests.get('http://api.sportradar.us/soccer-' + VERSION + '/na/teams/' + stats_id + '/profile.xml?api_key=' + API_KEY)
    soup = BeautifulSoup(r.content, "html.parser")
    manager = soup.find('manager')

    birthdate = manager['birthdate']
    if (birthdate != ""):
        dt = datetime.strptime(birthdate, "%Y-%m-%d")

    add_manager = ("INSERT INTO managers "
        "(first_name, last_name, country_code, country, preferred_foot, birthdate, height_in, weight_lb, height_cm, weight_kg, stats_id, team_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

    data_manager = (
        manager['first_name'], manager['last_name'], manager['country_code'], manager['country'], manager['preferred_foot'],
        birthdate, manager['height_in'], manager['weight_lb'], manager['height_cm'], manager['weight_kg'], manager["id"], id)

    cursor.execute(add_manager, data_manager)
    cnx.commit()

cursor.close()
cnx.close()



