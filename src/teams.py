import mysql.connector
import xml.etree.ElementTree as ET

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mls')
cursor = cnx.cursor()

add_team = ("INSERT INTO teams "
            "(name, full_name, alias, country_code, country, stats_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)")

tree = ET.parse("roster.xml")
root = tree.getroot()

for node in root.iter("tournament_group"):
    if (node.get("name") == "Major League Soccer"):
            for team in node.iter("team"):
                data_team = (
                    team.get("name"), team.get("full_name"), team.get("alias"), team.get("country_code"), team.get("country"), team.get("id"))
                cursor.execute(add_team, data_team)
                cnx.commit()


