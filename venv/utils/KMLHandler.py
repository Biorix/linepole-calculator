
from utils.Mesures import get_elevation as get_alt, get_distance_with_altitude as get_dist, get_subcoord_dist as sub_dist
from utils.Mesures import coordinates_solver as solver, AltitudeRetrievingError
from utils.Mesures import get_angle_between_two_lines as get_angle
from fastkml import kml, Document, Folder, Placemark
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from scipy import spatial

resolution = 25 #résolution pour déterminer l'altitude en metres
space_by_type = {'city':50, 'roads':100, 'hill':80, 'normal':100}

class KMLHandler(kml.KML):
    def __init__(self,kml_file):
        with open(kml_file, 'rb') as file:
            doc = file.read()
        super().__init__()
        self.from_string(doc)

        self.Documents = self._set_documents()
        self.Folders = self._set_folders(self.Documents)
        if self.Folders != None:
            self.Placemarks = self._set_placemarks(self.Folders)
        else:
            self.Placemarks = self._set_placemarks(self.Documents)

        self._set_dataframe()

    def _set_documents(self):
        return list(self.features())

    def _set_folders(self, upstream_features):
        for feature in upstream_features:
            if isinstance(list(feature.features())[0], Folder):
                return list(feature.features())
            else:
                return None

    def _set_placemarks(self, upstream_features):
        for feature in upstream_features:
            if isinstance(list(feature.features())[0], Placemark):
                return list(feature.features())
            else:
                return None

    def _set_dataframe(self):
        pmname = []
        pmcoords = []
        pmdesc = []
        for pm in self.Placemarks:
            if pm.geometry.geom_type == 'LineString':
                pmname1 = pm.name
                pmcoords1 = self._flip_longlat(pm.geometry.coords)
                if pm.description == None:
                    pmdesc1 = 'normal'
                else:
                    pmdesc1 = pm.description
            pmname.append(pmname1)
            pmcoords.append(pmcoords1)
            pmdesc.append(pmdesc1)

        info_df = pd.DataFrame()
        info_df['Trace'] = pmname
        info_df['Coordinates'] = pmcoords
        info_df['Type'] = pmdesc
        self.info_df = info_df
        self._set_sections()

    def _set_sections(self):
        func = lambda trace: Line(trace['Coordinates'],typekey=trace['Type'])
        self.info_df['pole_coords'] = self.info_df.apply(func, axis=1)

    def _flip_longlat(self, coordTuple):
        outList = []
        for coord in coordTuple:
            outList.append(tuple([coord[1],coord[0],coord[2]]))
        return tuple(outList)

    # def clearhead(self, doc):
    #     lines = doc.split('\n')
    #     for line in lines:
    #         if "encoding=" in line:
    #             lines.remove(line)
    #     return '\n'.join(lines)

    def set_section(self):
        typelist = self.info_df.desc.unique()

    #def output_coord(self):
        # a = self.df[self.df['descr'] == 'pole'][['long','lat','alt']].values.tolist()
        # b=' '.join(map(str,a))
        # c = b.replace('[','').replace(']','').replace(', ',',')
        # print(c)


class LineSection:
    def __init__(self, coord1, coord2, typekey='normal'):
        """
        Object that represent a section of LineString between two coordinates
        :param coord1: tuple or list:(lat, long)
        :param coord2: tupleor list:(lat, long)
        :param type: str: 'city', 'roads', 'hill'
        """
        self.start, self.stop, self.type = coord1, coord2, typekey
        self.df = pd.DataFrame(self._get_alt_profile(pole='y'), columns=['lat', 'long', 'alt', 'descr'])
        func = lambda row: self.distance_from_origine([row.lat, row.long, row.alt])
        self.df['dist_from_origin'] = self.df.apply(func,axis=1)
        self._set_prev_azi_angles()

    def __get__(self, instance, owner):
        return self.df

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.df.iloc[item]
        else:
            return self.df[self.df.index == item]

    def _get_alt_profile(self, pole='n'):
        "Slice the section to get elevation every $resolution meter"
        dist_evaluated, *_ = get_dist(list(self.start), list(self.stop))
        listCoord = sub_dist(self.start, self.stop, space_by_type[self.type], unit='m')
        alt = get_alt(listCoord)
        for i in range(len(alt)):
            listCoord[i][-1] = alt[i]
            if listCoord[i][:-1] == self.start[:-1]:
                listCoord[i].append('Start Point')
            elif listCoord[i][:-1] == self.stop[:-1]:
                listCoord[i].append('Stop Point')
            else:
                if pole == 'y':
                    listCoord[i].append('Pole')
                else:
                    listCoord[i].append('Altitude Profile')
        return listCoord

    def _get_pole_points(self):
        return self.df[self.df.desr == 'pole']

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
    # def _set_pole_points(self):
    #     dist_from_origin = 0
    #     templistCoordAlt = self.list_of_coord[1:]
    #     start = self[0][['lat','long','alt']].values.tolist()[0]
    #     index = 0
    #     while (self.total_dist - dist_from_origin) > 10:
    #         closestPoint = self.closest_coords([pole_lat, pole_long])
    #         index = closestPoint + 1
    #         self.insert_row([[pole_lat, pole_long, pole_alt, 'pole']], index)
    #         dist_from_origin = self.distance_from_origine([pole_lat, pole_long, pole_alt])
    #         self.df['dist_from_origin'][index] = dist_from_origin
    #         start = [pole_lat, pole_long, pole_alt]

    def _set_prev_azi_angles(self):
        angleList = [0]
        for index, row in self.df.iterrows():
            if index != 0:
                coord1 = row[['lat', 'long', 'alt']].values.tolist()
                coord2 = self[index -1][['lat', 'long', 'alt']].values.tolist()[0]
                _, angle = get_dist(coord1, coord2)
                angleList.append(angle)
        self.df['Azimut Angle'] = angleList


    list_of_coord = property(_get_list_of_coord)
    pole_points = property(_get_pole_points)
    total_dist = property(_get_total_dist)
   #max_angle = property(_get_max_angle)


class Line(LineSection):
    def __init__(self, list_of_coord, typekey='normal'):
        """
        Complete line composed of linesecions
        :param list_of_coord: list of list: (lat, long, alt)
        :param type: str: 'city', 'roads', 'hill'
        """
        self.start, self.stop, self.type = list_of_coord[0], list_of_coord[-1], typekey
        self.df = self._set_dataframe(list_of_coord)
        func = lambda row: self.distance_from_origine([row.lat, row.long, row.alt])
        self.df['dist_from_origin'] = self.df.apply(func,axis=1)
        self._set_prev_azi_angles()
        self._set_prev_hor_angles()

    def _set_dataframe(self, list_of_coord):
        ls_list = []
        for i in range(1, len(list_of_coord), 1):
            ls = LineSection(list_of_coord[i-1], list_of_coord[i],typekey=self.type)
            ls_list.append(ls[:-1])
        return pd.concat(ls_list, ignore_index=True, sort=False)

    def _set_prev_hor_angles(self):
        angle_list = [0]
        for i in range(1, len(self.list_of_coord)-1, 1):
            angle_list.append(get_angle(self.list_of_coord[i-1], self.list_of_coord[i], self.list_of_coord[i+1]))
        angle_list.append(0)
        self.df['Angle Horizontal'] = angle_list

if __name__ == "__main__":


    # line = Line([(11.63488448411825,-12.53838094890301),(11.63184216703874,-12.53958214076534),(11.62903433023975,-12.53552943917302),\
    #     (11.62872837445833,-12.53421506867161),(11.6283713707586,-12.53052930002481),(11.62707119983867,-12.52673726544863)])
    # # ls = LineSection((11.466135, -12.616524), ( 11.489022, -12.538672))
    # # close = ls.closest_coords([11.4667, -12.609])
    # #ls._set_pole_points()
    # print('OK')

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() # show an "Open" diaslog box and return the path to the selected file

    handle = KMLHandler(filename)