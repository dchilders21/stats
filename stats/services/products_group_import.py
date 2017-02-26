import pandas as pd
import re
from ast import literal_eval
import glob

"""categories = ['Harnesses', 'Tool Lanyards & Accessories', 'Fall Arresters', 'Energy Absorbing Lanyards', 'Lanyards',
              'Connectors', 'Rescue & rope access', 'Kits', 'Load Arresters', 'Kit Bags & Rucksacks', 'Non Fire Range',
              'ATEX Range']"""

all_list = []
all_dfs = pd.DataFrame()

category = 'Wire Rope Fittings & Sockets'

allFiles = glob.glob("concord/" + category + "/*.csv")

def parseName(str):
    #newCat = re.findall(r'"([^"]*)"', str)
    #newCat = re.sub('[^A-Za-z0-9]+', '', str)
    baseUrl = 'http://www.gtlifting.co.uk'

    df = pd.read_csv(str)

    img = literal_eval(df['product_image'][0])
    img_l = []

    for i in img:
        img_l.append(baseUrl + i)

    description = df['product_description'][0]
    print(description)
    description = literal_eval(description)

    df["description"] = df.apply(
        lambda row: "\n".join(description), axis=1)

    df["full_image"] = df.apply(
        lambda row: ", ".join(img_l), axis=1)

    df["category"] = df.apply(
        lambda row: category, axis=1)

    return df

for a in allFiles:
    all_list.append(parseName(a))

all_dfs = pd.concat(all_list)
all_dfs.to_csv("concord/" + category + "/all.csv")