import mysql.connector
import requests
from bs4 import BeautifulSoup
import settings
from datetime import datetime
from pytz import timezone
import pytz
from datetime import timezone

cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD,
                              host=settings.MYSQL_HOST,
                              database='nba')
cursor = cnx.cursor(buffered=True)

add_date = ("INSERT INTO games "
            "(scheduled_2) "
            "VALUES (%s)")

update_date = ("UPDATE ")



query = ("SELECT id, scheduled FROM games")
cursor.execute(query)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)



''' Loop through Games '''
for row in cursor.fetchall():
    #dt = utc_to_local(row[1])
    date = datetime.now(tz=pytz.utc)
    dt = row[1].astimezone(timezone('US/Pacific'))
    print(dt)
    '''cursor.execute("""UPDATE games SET scheduled_pst = %s WHERE id = %s""", (dt, row[0]))
    cnx.commit()'''