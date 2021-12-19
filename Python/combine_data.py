# load packages
import numpy as np
import pandas as pd
import os
import io
import re
import math
import csv

# get distance in kilometers
def get_distance(lat_1, lng_1, lat_2, lng_2):
    d_lat = lat_2 - lat_1
    d_lng = lng_2 - lng_1

    temp = (
         math.sin(d_lat / 2) ** 2
       + math.cos(lat_1)
       * math.cos(lat_2)
       * math.sin(d_lng / 2) ** 2
    )
    # radius of the earth: 6373.0km
    return 6373.0 * (2 * math.atan2(math.sqrt(temp), math.sqrt(1 - temp)))
# get_distance(lat_1, lng_1, lat_2, lng_2)

# function to convert to degrees in decimal format
# NOTE: do not forget to convert from degrees to radians
def dms2dd(s):
    # example: s = "0°51'"
    degrees, minutes = re.split("[°']", s)[:2]
    dd = float(degrees) + float(minutes)/60
    return dd
# dms2dd("0°51'") # test function

# load info on weather stations
stations = pd.read_csv('Data/weather_stations.csv', sep=",")

# convert lat and lon to degrees in decimal format
stations["geogr. Breite"] = stations["geogr. Breite"].apply(dms2dd)
stations["geogr. Länge"] = stations["geogr. Länge"].apply(dms2dd)

# compute distances for each combination and find nearest weather station for each stadion
stadiums = pd.read_csv('bundesliga_stadiums.csv', sep=",")
stadiums['team'] = stadiums['team'].str.strip()

# initialize variables
stadiums['min_dist'] = 10000
stadiums['nearest_station'] = ''

# iterate through all stadiums and stations and find the nearest station for each stadium
for index, row in stadiums.iterrows():
    lng_1, lat_1 = map(math.radians, [row.lon, row.lat])
    for index2, row2 in stations.iterrows():
        lng_2, lat_2 = map(math.radians, [row2['geogr. Länge'], row2['geogr. Breite']])
        d = get_distance(lat_1, lng_1, lat_2, lng_2)
        if d < stadiums['min_dist'][index]:
            stadiums.loc[index, 'nearest_station'] = row2['Stations_ID']
            stadiums.loc[index, 'min_dist'] = d

# load data on Bundesliag matches
matches = pd.read_csv('matches_cleaned_20_21.csv', sep=",")
matches = pd.concat([matches,
                     pd.read_csv('matches_cleaned_19_20.csv', sep=","),
                     pd.read_csv('matches_cleaned_18_19.csv', sep=","),
                     pd.read_csv('matches_cleaned_17_18.csv', sep=","),
                     pd.read_csv('matches_cleaned_16_17.csv', sep=",")]).reset_index(drop=True)
matches['home'] = matches['home'].str.strip()
matches['away'] = matches['away'].str.strip()

# read one dataset separately to have an initial dataset
all_weather = pd.read_csv('Data/zips/historical/01078/produkt_klima_tag_19520101_20201231_01078.txt', sep=';')

# iterate through the weather data for all relevant station and join it to the match data
for index, row in matches_station.iterrows():
    # get current station ID
    current_station = str(row['nearest_station'])

    # pad strings to 5 characters length
    if len(current_station) == 3:
        current_station = '00' + current_station
    elif len(current_station) == 4:
        current_station = '0' + current_station

    # get file with recent weather data
    dir_files = [f for f in os.listdir('Data/zips/recent/' + str(current_station)) if f.startswith('produkt')]

    # load weather data
    weather = pd.read_csv('Data/zips/recent/' + current_station + '/' + dir_files[0], sep=';')

    # add to weather data from other stations
    all_weather = pd.concat([all_weather, weather])

    # get file with historical weather data
    dir_files = [f for f in os.listdir('Data/zips/historical/' + str(current_station)) if f.startswith('produkt')]

    # load weather data
    weather = pd.read_csv('Data/zips/historical/' + current_station + '/' + dir_files[0], sep=';')

    # add to weather data from other stations
    all_weather = pd.concat([all_weather, weather])
    all_weather.drop_duplicates(subset=['STATIONS_ID', 'MESS_DATUM'], keep='first', inplace=True)

# combine match data with station and weather data
matches_station = pd.merge(matches, stadiums, left_on = 'home', right_on = 'team').sort_values('home').reset_index(drop=True)
matches_station_weather = pd.merge(matches_station, all_weather, how='left',
                               left_on = ['date_alt', 'nearest_station'],
                               right_on = ['MESS_DATUM', 'STATIONS_ID']).sort_values('home').reset_index(drop=True)

# create column holding total number of goals for a given match
matches_station_weather['score_total'] = matches_station_weather.home_score + matches_station_weather.away_score

# remove whitespace form column names
matches_station_weather.columns = matches_station_weather.columns.str.strip()

# set missing values to NaN
matches_station_weather.loc[matches_station_weather.RSK == -999, 'RSK'] = np.nan

# create temperature squared variable
matches_station_weather['TMK2'] = matches_station_weather['TMK']**2

# generate bins for RSK (Niederschlag) values
matches_station_weather['RSK_bin'] = 0
for index, row in matches_station_weather.iterrows():
    if matches_station_weather.loc[index, 'RSK'] == 0:
        matches_station_weather.loc[index, 'RSK_bin'] = 0
    elif matches_station_weather.loc[index, 'RSK'] < 5:
        matches_station_weather.loc[index, 'RSK_bin'] = 1
    elif matches_station_weather.loc[index, 'RSK'] < 10:
        matches_station_weather.loc[index, 'RSK_bin'] = 2
    elif matches_station_weather.loc[index, 'RSK'] < 15:
        matches_station_weather.loc[index, 'RSK_bin'] = 3
    elif matches_station_weather.loc[index, 'RSK'] < 20:
        matches_station_weather.loc[index, 'RSK_bin'] = 4
    elif matches_station_weather.loc[index, 'RSK'] < 25:
        matches_station_weather.loc[index, 'RSK_bin'] = 5
    elif matches_station_weather.loc[index, 'RSK'] < 30:
        matches_station_weather.loc[index, 'RSK_bin'] = 6
    else:
        matches_station_weather.loc[index, 'RSK_bin'] = 7

# generate bins for TSK (temperature) values
matches_station_weather['TMK_bin'] = 0
for index, row in matches_station_weather.iterrows():
    if matches_station_weather.loc[index, 'TMK'] < -10:
        matches_station_weather.loc[index, 'TMK_bin'] = -10
    elif matches_station_weather.loc[index, 'TMK'] < -5:
        matches_station_weather.loc[index, 'TMK_bin'] = -5
    elif matches_station_weather.loc[index, 'TMK'] < 0:
        matches_station_weather.loc[index, 'TMK_bin'] = 0
    elif matches_station_weather.loc[index, 'TMK'] < 5:
        matches_station_weather.loc[index, 'TMK_bin'] = 5
    elif matches_station_weather.loc[index, 'TMK'] < 10:
        matches_station_weather.loc[index, 'TMK_bin'] = 10
    elif matches_station_weather.loc[index, 'TMK'] < 15:
        matches_station_weather.loc[index, 'TMK_bin'] = 15
    elif matches_station_weather.loc[index, 'TMK'] < 20:
        matches_station_weather.loc[index, 'TMK_bin'] = 20
    elif matches_station_weather.loc[index, 'TMK'] < 25:
        matches_station_weather.loc[index, 'TMK_bin'] = 25
    else:
        matches_station_weather.loc[index, 'TMK_bin'] = 30
