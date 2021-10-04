# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 14:50:46 2021

@author: shali
"""

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os, glob 
import plotly.express as px
import warnings
warnings.filterwarnings(action = 'ignore')
import plotly.graph_objects as go
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc 
import dash_html_components as html

''' the dataset contains three json files named schedules.json, stations.json, and trains.json.
In stations.json, we can extract the coordinates of each stations corresponding to each station_code. 
trains.json file contains details of trains including from_station_code to to_station_code.

First task: 
    To plot the map containing details of trains traveling from one station to another. 

'''

# to get the path of json files
file_list = glob.glob(os.path.join(os.getcwd(), 'datasets', '*.json'))

data = dict()

# to load the dataset 
for path in file_list:
    data[path.split('\\')[-1].split('.')[0]] = pd.read_json(path)
    

# to extract from_station and to_station from data['trains'] dataset

from_station, to_station = [], []

for i in range(len(data['trains'])):
     from_station.append(data['trains']['features'][i]['properties']['from_station_code'])
     to_station.append(data['trains']['features'][i]['properties']['to_station_code'])

# to create a dictionary containing from_station and to_station
stations_dict = {'from_station': from_station, 'to_station':to_station}
station = pd.DataFrame(stations_dict)

print(data['stations']['features'][3])

# to extract each station coordinates from data['stations'] dataset

station_lat_lon = {}
for i in data['stations']['features']:
    code = i['properties']['code']
    try:
        if code not in station_lat_lon:
            station_lat_lon[code] = i['geometry']['coordinates']
    except:
        continue 


from_lat, to_lat, from_lon, to_lon =[], [], [], []

for i in range(len(station)): 
    from_loc = station['from_station'][i]
    to_loc = station['to_station'][i]
    
    if from_loc in station_lat_lon:
        from_lat.append(station_lat_lon[from_loc][1])
        from_lon.append(station_lat_lon[from_loc][0])
    
    else:
        from_lat.append(np.nan)
        from_lon.append(np.nan)
    
    if to_loc in station_lat_lon:
        to_lat.append(station_lat_lon[to_loc][1])
        to_lon.append(station_lat_lon[to_loc][0])
        
    else:
        to_lat.append(np.nan)
        to_lon.append(np.nan)

station['from_lat'] = pd.Series(from_lat)
station['from_lon'] = pd.Series(from_lon)
station['to_lat'] = pd.Series(to_lat)
station['to_lon'] = pd.Series(to_lon)

station.isnull().sum()

station.dropna(inplace = True)

station.reset_index(inplace = True)



fig = go.Figure()
df = pd.read_csv("https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/active_cases_2020-07-17_0800.csv")
z = np.ones_like(df['state']) * 200

fig = go.Figure(data=go.Choropleth(
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
    featureidkey='properties.ST_NM',
    locationmode='geojson-id',
    locations=df['state'],
    z=z,
    autocolorscale=False,
    colorscale='Blues',
    marker_line_color='peachpuff',
))

train_paths = []
for i in range(len(station)):
    fig.add_trace(
        go.Scattergeo(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',
            locationmode='geojson-id',
            lon = [station['from_lon'][i], station['to_lon'][i]],
            lat = [station['from_lat'][i], station['to_lat'][i]],
            text = station['from_station'][i],
            mode = 'lines',
            line = dict(width = 1,color = 'red'),
            opacity = 0.1
        )
    )

fig.update_geos(
    visible=False,
    projection=dict(
        type='conic conformal',
        parallels=[12.472944444, 35.172805555556],
        rotation={'lat': 24, 'lon': 80}
    ),
    lonaxis={'range': [68, 98]},
    lataxis={'range': [6, 38]}
)

fig.update_layout(
    title=dict(
        text="Trains travelled between different locations in India",
        xanchor='center',
        x=0.5,
        yref='paper',
        yanchor='bottom',
        y=1,
        pad={'b': 10}
    ),
    margin={'r': 0, 't': 30, 'l': 0, 'b': 0},
    height=550,
    coloraxis_showscale=False,
    width=550
    
)

fig.update_traces(showlegend=False)


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False) 
