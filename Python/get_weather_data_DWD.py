# load packages
import numpy as np
# import pandas as pd
import os
import urllib.request
from bs4 import BeautifulSoup
import requests, zipfile, io
import re

# set index url
# index_url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/"
index_url = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/"

# access index of data for German weather stations
handle = urllib.request.urlopen(index_url).read()
soup = BeautifulSoup(handle, "html.parser")

# extract the anchor elements
tags = soup.findAll('a', href=True)

# get the links to the zip files for all weather stations
files = []
for link in tags:
    if link['href'].startswith('tageswerte'):
        files.append(link['href'])

# download all the zip files
for file in files:
    station_id = re.findall(r'_([0-9]*)_', file)[0]
    r = requests.get(index_url + file)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # z.extractall("./zips/historical/" + station_id)
    z.extractall("./Data/zips/recent/" + station_id)
