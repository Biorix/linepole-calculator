# -*- coding: utf-8 -*-
from fastkml import kml, Document, Folder, Placemark, styles
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
from tqdm import trange, tqdm
import random
from colour import Color
import numpy as np

ns = '{http://www.opengis.net/kml/2.2}'

def openKML(kml_file):
    with open(kml_file,  'rb') as file:
        doc = file.read()
    KML = kml.KML()
    KML.from_string(doc)
    return KML

def gen_placemark_from_Line(coords, ns, names):
    """
    create a placemark object for kml
    :param coords: list of the base line and optionaly the offsets lines
    :type coords: list of coordinates
    :param ns: ns of kml version
    :type ns: str
    :param name: list of line names
    :type name: list of str
    :return: list of placemark object
    :rtype: list of placemark
    """
    outplacemarks = []
    name_l = [name for name in names if 'offset_l' in name]
    name_r = [name for name in names if 'offset_r' in name]
    name_b = [name for name in names if 'offset_r' not in name and 'offset_l' not in name]
    coords_l = [coords[names.index(name)] for name in names if 'offset_l' in name]
    coords_r = [coords[names.index(name)] for name in names if 'offset_r' in name]
    dim = len(coords_r)
    coords_b = [coords[names.index(name)] for name in names if 'offset_r' not in name and 'offset_l' not in name]
    colors = color_range_gen(dim+1)
    for i in range(dim):
        ls = styles.LineStyle(ns=ns, id=None, color=colors[i+1], width=1.5)
        s1 = styles.Style(styles=[ls])
        outplacemark_l = kml.Placemark(ns, None, name_l[i], None, styles=[s1])
        outplacemark_r = kml.Placemark(ns, None, name_r[i], None, styles=[s1])
        outplacemark_l.geometry = LineString(coords_l[i])
        outplacemark_r.geometry = LineString(coords_r[i])
        outplacemarks.append(outplacemark_l)
        outplacemarks.append(outplacemark_r)
    ls = styles.LineStyle(ns=ns, id=None, color=colors[0], width=3)
    s1 = styles.Style(styles=[ls])
    outplacemark = kml.Placemark(ns, None, name_b[0], None, styles=[s1])
    outplacemark.geometry = LineString(coords_b[0])
    outplacemarks.append(outplacemark)

    return outplacemarks


def random_color_gen():
    """
    Generate random color in kml format
    :return generated color
    :rtype str
    """
    r = lambda: random.randint(0, 255)
    return 'ff%02X%02X%02X' % (r(), r(), r())


def color_range_gen(range_):
    """
    Generate random color range in kml format
    :param length of the wanted color range
    :type int
    :return generated color
    :rtype list of str
    """
    base = Color(random_color_gen().replace('ff', '#', 1))
    finale = Color(random_color_gen().replace('ff', '#', 1))
    output_colors = []
    for c in list(base.range_to(finale, range_)):
        c = '%s' % c
        output_colors.append(c.replace('#', 'ff', 1))

    return output_colors


def extract_info_from_df(df):
    line_list = []
    section_list = []
    start_lat_list = []
    start_lon_list = []
    stop_lat_list = []
    stop_lon_list = []

    lines = df['Trace'].unique().tolist()
    for line in lines:
        coords = df[df.Trace == line]['Coordinates'].tolist()[0]
        for i in range(0, len(coords)-1):
            start_lat, stop_lat = coords[i][0], coords[i+1][0]
            start_lon, stop_lon = coords[i][1], coords[i + 1][1]
            section_name = line + '-' + str(lines.index(line))
            start_lat_list.append(start_lat)
            start_lon_list.append(start_lon)
            stop_lat_list.append(stop_lat)
            stop_lon_list.append(stop_lon)

            section_list.append(section_name)
            line_list.append(line)

    df_out = pd.DataFrame({'Line': line_list,'Section': section_list, 'start_lat': start_lat_list,
                           'start_lon': start_lon_list, 'stop_lat': stop_lat_list, 'stop_lon': stop_lon_list})
    return df_out

