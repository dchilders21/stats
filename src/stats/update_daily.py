import mysql.connector
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from datetime import datetime, date, time
import time
import sys
import os

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor(buffered=True)

API_KEY = "b99x88uxzrfbvm9kxtfmabth"
VERSION = "t2"
DATE = "2016/09/12"

add_team = ("INSERT INTO matches "
            "(stats_id, status, scheduled, scratched, home_id, away_id, venue_id, round_number, round_week) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")

r = requests.get("http://api.sportradar.us/soccer-" + VERSION + "/na/matches/" + DATE + "/schedule.xml?api_key=" + API_KEY)
soup = BeautifulSoup(r.content, "html.parser")
#soup = BeautifulSoup(open("schedule_eu.xml"), "html.parser")

matches = soup.find_all('match')

for match in matches:
    #category = match.find('category')
    league = match.find('tournament_group')

    #if category["name"] == "France":

    if league["name"] == "Major League Soccer":
        print(match['id'])

        query = ("SELECT id FROM matches "
                 "WHERE stats_id = %(match_id)s")
        cursor.execute(query, {'match_id': match["id"]})

        if cursor.rowcount != 0:
            print("Match ID already exists in DB")
        else:
            home = match.find("home")["id"]
            away = match.find("away")["id"]
            venue = match.find("venue")["id"]
            round_number = match.find("round")["number"]
            round_week = match.find("round")["week"]

            schedule = match["scheduled"][:-1]
            dt = datetime.strptime(schedule, "%Y-%m-%dT%H:%M:%S")

            scratched = int(match["scratched"] == 'true')

            query = ("SELECT id FROM teams "
                     "WHERE stats_id = %(home_id)s")

            cursor.execute(query, {'home_id': home})

            for id in cursor:
                home_id = id[0]

            query = ("SELECT id FROM teams "
                         "WHERE stats_id = %(away_id)s")
            cursor.execute(query, {'away_id': away})

            for id in cursor:
                away_id = id[0]

            data_team = (
                match["id"], match["status"], dt, scratched, home_id,
                away_id, match["id"], round_number, round_week)

            cursor.execute(add_team, data_team)
            cnx.commit()






