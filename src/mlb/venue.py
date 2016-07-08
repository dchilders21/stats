import json, requests
import mysql.connector

cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='mlb')
cursor = cnx.cursor()

API_KEY = "patymcysmye3a82xp5kf5ba4"
VERSION = "t5"

r = requests.get('https://api.sportradar.us/mlb-' + VERSION + '/league/venues.json?api_key=' + API_KEY)
data = r.text
json_data = json.loads(data)
add_venue = ("INSERT INTO venues "
                "(stats_id, name, capacity, surface, address, city, state, zip, country, lf, lcf, cf, rcf, rf, mlf, mlcf, mrcf, mrf) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

for venue in json_data["venues"]:
    venue_att = {'state': "", 'capacity': "", 'surface': "", 'address': "", 'city': "", 'zip': ""}
    venue_dist = {'lcf': "", 'rcf': "", 'mlf': "", 'mlcf': "", 'mrcf': "", 'mrf': "", 'lf': "", 'cf': "", 'rf': "" }

    for att in venue_att:
        if att in venue:
            venue_att[att] = venue[att]
        else:
            venue_att[att] = ""

    for dist in venue["distances"]:
        if dist in venue["distances"]:
            venue["distances"][dist] = venue["distances"][dist]
        else:
            venue["distances"][dist] = ""

    data_venue = (venue["id"], venue["name"], venue_att["capacity"], venue_att["surface"], venue_att["address"], venue_att["city"], venue_att["state"], venue_att["zip"], venue["country"], venue_dist["lf"], venue_dist["lcf"], venue_dist["cf"], venue_dist["rcf"], venue_dist["rf"], venue_dist["mlf"], venue_dist["mlcf"], venue_dist["mrcf"], venue_dist["mrf"])
    cursor.execute(add_venue, data_venue)
    cnx.commit()

cursor.close()
cnx.close()