
from utils.Mesures import get_elevation as get_alt, get_distance_with_altitude as get_dist, get_subcoord_dist as sub_dist
from utils.Mesures import coordinates_solver as solver, AltitudeRetrievingError
from pykml import parser
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy import spatial

resolution = 25 #résolution pour déterminer l'altitude en metres
space_by_type = {'city':50, 'roads':100, 'hill':80, 'normal':100}

class KMLHandler:
    def __init__(self,kml_file):
        with open(kml_file) as kml:
            try:
                folder = parser.parse(kml).getroot().Document.Folder
            except:
                folder = parser.parse(kml).getroot().Document

        plnm = []
        cordi = []
        desc = []
        for pm in folder.Placemark:
            plnm1 = pm.name
            plcs1 = pm.LineString.coordinates
            try:
                pldesc = pm.LineString.description
            except:
                pldesc = 'None'
            plnm.append(plnm1.text.replace('\n','').replace('\t',''))
            cordi.append(plcs1.text.replace('\n','').replace('\t',''))
            desc.append(pldesc)

        db = pd.DataFrame()
        db['Trace'] = plnm
        db['coordinates'] = cordi
        db['Desciption'] = desc
        db['Longitude'], db['Latitude'], db['value'] = zip(*db['coordinates'].apply(lambda x: x.split(',', 2)))
        self.db = db

        self.sections = []

    #def addSection(self):
        self

    #def output_coord(self):
        # a = self.df[self.df['descr'] == 'pole'][['long','lat','alt']].values.tolist()
        # b=' '.join(map(str,a))
        # c = b.replace('[','').replace(']','').replace(', ',',')
        # print(c)

class LineSection:
    def __init__(self, coord1, coord2, typekey='normal'):
        """
        Object that represent a section of LineString between two coordinates
        :param coord1: tuple:(lat, long)
        :param coord2: tuple:(lat, long)
        :param type: str: 'city', 'roads', 'hill'
        """
        self.start, self.stop, self.type = coord1, coord2, typekey
        self.df = pd.DataFrame(self._get_alt_profile(), columns=['lat', 'long', 'alt', 'descr'])
        func = lambda row: self.distance_from_origine([row.lat, row.long, row.alt])
        self.df['dist_from_origin'] = self.df.apply(func,axis=1)

    def __getitem__(self, item):
        return self.df[self.df.index == item]

    def _get_alt_profile(self):
        "Slice the section to get elevation every $resolution meter"
        dist_evaluated, *_ = get_dist(list(self.start) + [0], list(self.stop) + [0])
        listCoord = sub_dist(self.start, self.stop, space_by_type[self.type], unit='m')
        alt = get_alt(listCoord)
        for i in range(len(alt)):
            listCoord[i].append(alt[i])
            if listCoord[i] == self.start:
                listCoord[i].append('Start Point')
            elif listCoord[i] == self.stop:
                listCoord[i].append('Stop Point')
            else:
                listCoord[i].append('Altitude Profile')
        return listCoord

    def _get_total_dist(self, list_of_coordAlt=None):
        tot_dist = 0
        if list_of_coordAlt == None:
            list_of_coordAlt = self._get_list_of_coord()

        for i in range(len(list_of_coordAlt)-1):
            tot_dist += get_dist(list_of_coordAlt[i], list_of_coordAlt[i+1])[0]
        return tot_dist

    def _get_list_of_coord(self):
        return self.df[['lat','long','alt']].values.tolist()

    def distance_from_origine(self, coord):
        """
        :return the distance from the first point
        """
        index = self.df.loc[(self.df['lat'] == coord[0]) & (self.df['long'] == coord[1])].index.values[0]
        listCoordAlt = self.df[self.df.index <= index][['lat','long','alt']].values.tolist()
        return self._get_total_dist(listCoordAlt)


    def closest_coords(self, coord):
        """:return closest coordinates index"""
        list_of_coord = self.df[['lat','long']].values.tolist()
        tree = spatial.KDTree(list_of_coord)
        _, index = tree.query([[coord]])

        return index[0][0]

    def insert_row(self, row_value, index):
        """
        Insert a new row at the determined index
        :param row_value: list of value to insert as: ['lat', 'long', 'alt', 'descr']
        :param index: index where the row will be inserted
        """
        row = pd.DataFrame(row_value, columns=['lat', 'long', 'alt', 'descr'])
        self.df = pd.concat([self.df.iloc[:index], row, self.df.iloc[index:]]).reset_index(drop=True)


    # TODO: insert new indexes to the right place
    def _set_pole_points(self):
        dist_from_origin = 0
        templistCoordAlt = self.list_of_coord[1:]
        start = self[0][['lat','long','alt']].values.tolist()[0]
        index = 0
        while (self.total_dist - dist_from_origin) > 10:
            closestPoint = self.closest_coords([pole_lat, pole_long])
            index = closestPoint + 1
            self.insert_row([[pole_lat, pole_long, pole_alt, 'pole']], index)
            dist_from_origin = self.distance_from_origine([pole_lat, pole_long, pole_alt])
            self.df['dist_from_origin'][index] = dist_from_origin
            start = [pole_lat, pole_long, pole_alt]




    list_of_coord = property(_get_list_of_coord)
    pole_points = property(_set_pole_points)
    total_dist = property(_get_total_dist)
   #max_angle = property(_get_max_angle)


if __name__ == "__main__":
    
    ls = LineSection((11.466135, -12.616524), ( 11.489022, -12.538672))
    close = ls.closest_coords([11.4667, -12.609])
    #ls._set_pole_points()
    print('OK')

# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# filename = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
#
# handle = KMLHandler(filename)