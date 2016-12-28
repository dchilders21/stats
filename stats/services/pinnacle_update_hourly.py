import requests
from fake_useragent import UserAgent
import datetime
from stats import model_libs
from os.path import dirname, abspath
import os
import pandas as pd

t = model_libs.tz2ntz(datetime.datetime.utcnow(), 'UTC', 'US/Pacific').strftime("%m_%d_%y")
today = datetime.datetime.strptime(t, '%m_%d_%y')
ua = UserAgent()
headers = {'User-Agent': ua.random}
url = 'https://www.pinnacle.com/webapi/1.15/api/v1/GuestLines/NonLive/4/487'

r = requests.get(url, headers=headers)
json = r.json()
current_path = dirname(dirname(abspath(__file__)))

if not os.path.isdir(current_path + '/csv/pinnacle/' + t + '/'):
    print('Making New Directory {} for the CSV in Pinnacle'.format(t))
    os.makedirs(current_path + '/csv/pinnacle/' + t + '/')


df = pd.DataFrame([], columns=['team_1', 'team_2', 'over_under', 'spread'])

for line in json['Leagues'][0]['Events']:

    # Period Number 0 are the lines used on the guest site
    if line['PeriodNumber'] == 0:
        d = line['DateAndTime'].split('T', 1)[0]
        gametime = datetime.datetime.strptime(d, '%Y-%m-%d')
        # Need to make sure we are only pulling today's games for now.
        if today == gametime:

            lns = {'team_1': line['Participants'][0]['Name'], 'team_2': line['Participants'][1]['Name'],
                   'over_under': line['Totals']['Min'], 'spread': line['Participants'][0]['Handicap']['Min']}

            df = df.append(lns, ignore_index=True)

df.to_csv(current_path + '/csv/pinnacle/' + t + '/pinnacle_lines.csv')



