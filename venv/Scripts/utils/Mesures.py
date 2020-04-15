import requests
import pandas as pd
import json
from geopy import distance
import math

# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM
def get_elevation(lat, long):
    query = (r'https://api.open-elevation.com/api/v1/lookup\?locations\={0},{1}'.format(lat, long))
    r = requests.get(query)
    r =  json.load(r)
    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
    return elevation

def distance_with_altitude(coord1, coord2, unit='m'):
    """
    Give the distance relative to altitude between two coordinates
    the altitude must be provided in the same unit as the one supplied (default : m)
    :param coord1: tuple:(float:latitude, float:longitude, float:altitude)
    :param coord2: tuple:(float:latitude, float:longitude, float:altitude)
    :param unit: string:name of the returned unit i.e : "km", "miles", "m"
    :return: distance in the selected unit
    """
    lat1, long1, alt1 = coord1
    lat2, long2, alt2 = coord2
    x_dist = eval('distance.geodesic((lat1,long1),(lat2, long2)).{0}'.format(unit))
    y_dist = abs(alt2 - alt1)
    hypothenus = math.sqrt(x_dist**2 + y_dist**2)
    return hypothenus




if __name__ == "__main__":
    #get_elevation(11.430555, -12.682673)
    print(distance_with_altitude((11.447561, -12.672399, 1008),(11.446225,-12.672896,1052),unit='m'))