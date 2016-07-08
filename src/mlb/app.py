import json, requests
from flask import Flask
import mysql.connector

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mlb')
cursor = cnx.cursor()


app = Flask(__name__)

API_KEY = "patymcysmye3a82xp5kf5ba4"
VERSION = "t5"

@app.route('/')
def create_teams():
    r = requests.get('https://api.sportradar.us/mlb-' + VERSION + '/league/depth_charts.json?api_key=' + API_KEY)
    data = r.text
    json_data = json.loads(data)
    add_team = ("INSERT INTO teams "
                    "(name, abbr, market, stats_id) "
                    "VALUES (%s, %s, %s, %s)")
    for team in json_data["teams"]:
        data_team = (team["name"], team["abbr"], team["market"], team["id"])
        # Insert new team
        cursor.execute(add_team, data_team)
        cnx.commit()
    return "hello"

    cursor.close()
    cnx.close()

if __name__ == "__main__":
    app.run()