# -*- coding: utf-8 -*-
import requests
import pandas as pd
import json
from geopy import distance
import math
from scipy.optimize import fsolve
import subprocess

r_earth = 6371.009


class AltitudeRetrievingError(Exception):
    def __init__(self, err, list):
        self.err = err
        self.list = list
        self.message = ("Error while getting elevation :", err, '\n arguments : {0}'.format(list))


# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM
def get_elevation(coordList):
    coordList = [list(i) for i in coordList]
    proc = subprocess.Popen(["curl","-d", str(coordList), "-XPOST", "-H", "Content-Type: application/json", \
        "https://elevation.racemap.com/api" ], stdout=subprocess.PIPE, shell=True)
    (elevation, err) = proc.communicate()

    if err == None and b'Too Many Request' not in elevation:
        return eval(elevation)
    elif b'Too Many Request' in elevation:
        return get_elevation(coordList)
    else:
        print("Error while getting elevation :", err, elevation)
        raise AltitudeRetrievingError(err,coordList)

def addToCoord(coord, dx, dy, unit='m'):
    if unit == 'm':
        dx /= 1000
        dy /= 1000
        latitude, longitude, *alt = coord
        new_latitude = latitude + (dy / r_earth) * (180 / math.pi)
        new_longitude = longitude + (dx / r_earth) * (180 / math.pi) / math.cos(latitude * math.pi / 180)
    return [new_latitude, new_longitude, alt]

def get_distance_with_altitude(coordAlt1, coordAlt2, unit='m'):
    """
    Give the distance relative to altitude between two coordinates
    the altitude must be provided in the same unit as the one supplied (default : m)
    :param coord1: tuple:(float:latitude, float:longitude, float:altitude)
    :param coord2: tuple:(float:latitude, float:longitude, float:altitude)
    :param unit: string:name of the returned unit i.e : "km", "miles", "m"
    :return: (distance, angle) in the selected unit and degrees
    """
    lat1, long1, alt1 = coordAlt1
    lat2, long2, alt2 = coordAlt2
    if alt1 == 0 or alt2 == 0:
        return distance.geodesic(coordAlt1[:-1], coordAlt2[:-1]).m, 0
    x_dist = eval('distance.geodesic((lat1,long1),(lat2, long2)).{0}'.format(unit))
    y_dist = abs(alt2 - alt1)
    hypothenus = math.sqrt(x_dist**2 + y_dist**2)
    angle = math.degrees(math.atan(y_dist / x_dist))
    return hypothenus, angle

# def coordinates_solver(wanted_dist, start_point, list_coordAlt, precrep=1000000):
#     """
#     Recursive solver that find the coordinates separated by the wanted distance from the start point
#     :param wanted_dist: float: distance between the start_point coordinates and the searched coord
#     :param start_point: list: [lat, long] of the starting point
#     :param list_coordAlt: list: [[lat, liong, alt], ...] list of available points precalculated
#     :param precrep: closest previosly find distance (for recursive purpose, DO NOT USE)
#     :return: list: list of closest coordinates [lat, long, alt]
#     """
#     func = lambda dist : wanted_dist - dist
#     distances = [get_distance_with_altitude(start_point, coordAlt)[0] for coordAlt in list_coordAlt]
#     for guess in distances:
#         if abs(func(guess)) <= abs(precrep):
#             precrep = func(guess)
#             closest = list_coordAlt[distances.index(guess)]
#             _, _ , theta = get_xy_ground_distance(start_point, closest)
#             dx = math.cos(theta) * precrep
#             dy = math.sin(theta) * precrep
#             next_dist_coord = addToCoord(closest[:-1], dx, dy, unit='m')
#
#     if abs(precrep) <= 5:
#         return closest
#     else:
#         #todo: corriger la non création de closest dans certain cas
#         try:
#             subcoord = get_subcoord_dist(start_point[:-1], next_dist_coord, precrep/10)
#         except:
#             closest = list_coordAlt[distances.index(guess)]
#             _, _, theta = get_xy_ground_distance(start_point, closest)
#             dx = math.cos(theta) * precrep
#             dy = math.sin(theta) * precrep
#             next_dist_coord = addToCoord(closest[:-1], dx/2, dy/2, unit='m')
#             subcoord = get_subcoord_dist(start_point[:-1], next_dist_coord, precrep / 10)
#         try:
#             Alt = get_elevation(subcoord)
#         except AltitudeRetrievingError:
#             raise
#         for i in range(len(subcoord)):
#             subcoord[i].append(Alt[i])
#         # on ajout cette liste de coordonnées à la précédente
#         closest = coordinates_solver(wanted_dist, start_point, subcoord[1:], precrep=precrep)
#         return closest

def get_xy_ground_distance(coord1, coord2, unit='m'):
    y_dist = distance.geodesic(coord1, (coord2[0],coord1[1])).m
    x_dist = distance.geodesic(coord1, (coord1[0], coord2[1])).m
    angle = math.atan2(y_dist,x_dist)
    return x_dist, y_dist, angle

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
    if coord2[0] < coord1[0]:
        y_dist *= -1
    x_dist = distance.geodesic(coord1, (coord1[0], coord2[1])).m
    if coord2[1] < coord1[1]:
        x_dist *= -1
    if x_dist < 0 or y_dist < 0:
        angle = math.atan2(y_dist, x_dist)
    else:
        angle = math.atan(y_dist/ x_dist)
    dy = math.sin(angle) * space
    dx = math.cos(angle) * space

    number = abs(int(dist_tot // space))
    coordList = [list(coord1)]
    for i in range(number):
        coordList.append(addToCoord(coordList[i],dx,dy))
    if dist_tot % space != 0:
        coordList.append(list(coord2))
    return coordList


def get_angle_between_two_lines(coord1, coord2, coord3):
    _, _, angle1 = get_xy_ground_distance(coord1, coord2)
    _, _, angle2 = get_xy_ground_distance(coord2, coord3)
    return abs(math.degrees(angle2) - math.degrees(angle1))

if __name__ == "__main__":
    #get_elevation(11.430555, -12.682673)
    listTest = [[11.466135, -12.616524, 0],[11.489022, -12.538672, 0]]
    start = [11.466135, -12.616524, 0]
    print(coordinates_solver(50,start, listTest[1:]))
    print(get_distance_with_altitude((11.447561, -12.672399, 1008),(11.446225,-12.672896,1052),unit='m'))
    a = get_elevation([[11.447561, -12.672399],[11.446225,-12.672896]])
    print(get_subcoord_dist((11.447561, -12.672399),(11.446225,-12.672896),5))