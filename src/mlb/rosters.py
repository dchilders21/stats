import json, requests
import mysql.connector

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mlb')
cursor = cnx.cursor()

API_KEY = "patymcysmye3a82xp5kf5ba4"
VERSION = "t5"

r = requests.get('https://api.sportradar.us/mlb-' + VERSION + '/league/full_rosters.json?api_key=' + API_KEY)

data = r.text
json_data = json.loads(data)
add_team = ("INSERT INTO rosters "
                "(stats_id, status, position, first_name, last_name, preferred_name, jersey_number, full_name, mlbam_id, height, weight, throw_hand, bat_hand, high_school, birthdate, birthstate, birthcountry, birthcity, pro_debut, updated, team_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
for team in json_data["teams"]:
    # Need to Query the Team Id
    query = ("SELECT id FROM teams "
             "WHERE stats_id = %(team_id)s")
    cursor.execute(query, { 'team_id': team["id"] })

    for id in cursor:
        key_id = id

    #'player_att' is for missing content in the return call
    player_att = {'birthstate': "", 'pro_debut': "", 'high_school': "", 'mlbam_id': ""}
    for player in team["players"]:

        for key in player:
            for att in player_att:
                if att in player:
                    player_att[att] = player[key]
                else:
                    player_att[att] = ""

        data_team = (player["id"], player["status"], player["position"], player["first_name"], player["last_name"], player["preferred_name"], player["jersey_number"], player["full_name"], player_att["mlbam_id"], player["height"], player["weight"], player["throw_hand"], player["bat_hand"], player_att["high_school"], player["birthdate"], player_att["birthstate"], player["birthcountry"], player["birthcity"], player_att["pro_debut"], player["updated"], key_id[0])
        # Insert Roster
        cursor.execute(add_team, data_team)
        cnx.commit()

cursor.close()
cnx.close()