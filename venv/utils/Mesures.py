# -*- coding: utf-8 -*-
import requests
import pandas as pd
import json
from geopy import distance
import math

r_earth = 6371.009

# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM
def get_elevation(coordList):
    elevation = []
    for lat, long in coordList:
        query = (r'https://elevation.racemap.com/api/?lat={0}&lng={1}'.format(lat, long))
        r = requests.get(query)
        elevation.append(float(r.text))
    return elevation

def addToCoord(coord, dx, dy):
    latitude, longitude = coord
    new_latitude = latitude + (dy / r_earth) * (180 / math.pi)
    new_longitude = longitude + (dx / r_earth) * (180 / math.pi) / math.cos(latitude * math.pi / 180)
    return new_latitude, new_longitude

def get_distance_with_altitude(coord1, coord2, unit='m'):
    """
    Give the distance relative to altitude between two coordinates
    the altitude must be provided in the same unit as the one supplied (default : m)
    :param coord1: tuple:(float:latitude, float:longitude, float:altitude)
    :param coord2: tuple:(float:latitude, float:longitude, float:altitude)
    :param unit: string:name of the returned unit i.e : "km", "miles", "m"
    :return: (distance, angle) in the selected unit and degrees
    """
    lat1, long1, alt1 = coord1
    lat2, long2, alt2 = coord2
    x_dist = eval('distance.geodesic((lat1,long1),(lat2, long2)).{0}'.format(unit))
    y_dist = abs(alt2 - alt1)
    hypothenus = math.sqrt(x_dist**2 + y_dist**2)
    angle = math.degrees(math.tan(y_dist / x_dist))
    return hypothenus, angle

def get_subcoord_dist(coord1, coord2, space, unit='m'):
    """
    Give coordinates between two coordinates seperated by the given distance
    :param coord1: float: first coord
    :param coord2: float: second coord
    :param distance: distance in given unit (default meter)
    :param unit: string:name of the returned unit i.e : "km", "miles", "m"
    :return: a list of coordinates
    """
    dist_tot = distance.geodesic(coord1, coord2).m
    y_dist = distance.geodesic(coord1, (coord2[0],coord1[1])).m
    x_dist = distance.geodesic(coord1, (coord1[0], coord2[1])).m
    angle = math.atan(y_dist / x_dist)
    dy = math.sin(angle) * space
    dx = math.cos(angle) * space

    number = int(dist_tot // space)
    coordList = [coord1]
    for i in range(number):
        coordList.append(addToCoord(coord1,dx,dy))
    if dist_tot % space != 0:
        coordList.append(coord2)
    return coordList

if __name__ == "__main__":
    #get_elevation(11.430555, -12.682673)
    print(get_distance_with_altitude((11.447561, -12.672399, 1008),(11.446225,-12.672896,1052),unit='m'))
    a = get_elevation([(11.447561, -12.672399),(11.446225,-12.672896)])
    print(get_subcoord_dist((11.447561, -12.672399),(11.446225,-12.672896),5))