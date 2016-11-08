import mysql.connector
import xml.etree.ElementTree as ET
import settings

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database=settings.MYSQL_DATABASE)
cursor = cnx.cursor()

add_team = ("INSERT INTO teams "
            "(name, full_name, alias, country_code, country, stats_id) "
            "VALUES (%s, %s, %s, %s, %s, %s)")

tree = ET.parse("team_hierarchy_eu.xml")
root = tree.getroot()

for node in root.iter("tournament_group"):
    if (node.get("name") == "Ligue 1"):
            for team in node.iter("team"):
                data_team = (
                    team.get("name"), team.get("full_name"), team.get("alias"), team.get("country_code"), team.get("country"), team.get("id"))
                cursor.execute(add_team, data_team)
                cnx.commit()


