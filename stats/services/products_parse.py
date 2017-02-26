import pandas as pd
import re
import glob

categories = ['Grade 8 Lifting Sets Components for Offshore Containers', 'Grade 8 Fram Links and Hooks', 'Grade 80 Chain and Fittings',
 'Grade 10 Chain and Fittings', 'Hoisting and Material Handling', 'Hydraulics', 'Shackles', 'Polyester Slings & Assemblies',
 'Wire Rope Fittings & Sockets', 'Swivels', 'Eyebolts and Eyenuts', 'Chain', 'Loadbinding Equipment', 'Fishing Equipment',
 'Rigging Screws/Turnbuckles', 'Lashing Equipment', 'Miscellaneous/Deck Plates', 'Stainless Steel Equipment', 'Height Safety']

all_list = []
all_dfs = pd.DataFrame()

def parseName(str):
    print(str)
    #newCat = re.findall(r'"([^"]*)"', str)
    newCat = re.sub('[^A-Za-z0-9]+', '', str)
    print(newCat)
    #baseUrl = 'http://www.gtlifting.co.uk'

    print(newCat)
    df = pd.read_csv('concord/Category_Adj/' + newCat + '_Adj.csv')
    df["parent_category"] = df.apply(
        lambda row: str, axis=1)
    return df

for c in categories:
    all_list.append(parseName(c))

all_dfs = pd.concat(all_list)
all_dfs.to_csv("concord/all_dfs.csv")