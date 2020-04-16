
from utils.Mesures import get_elevation as get_alt, get_distance_with_altitude as get_dist, get_subcoord_dist as sub_dist
from pykml import parser
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

resolution = 50 #résolution pour déterminer l'altitude en metres

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

    def addSection(self):
        self

    def output_coord(self):


class LineSection:
    def __init__(self, coord1, coord2, type='normal'):
        """
        Object that represent a section of LineString between two coordinates
        :param coord1: tuple:(lat, long)
        :param coord2: tuple:(lat, long)
        :param type: str: 'city', 'roads', 'hill'
        """
        self.start, self.stop, self.type = coord1, coord2, type

    def _slicing_line_(self):
        "Slice the section to get elevation every $resolution meter"
        self._sliced_line_ = sub_dist(self.start, self.stop, resolution, unit='m')

    def _get_elevation_(self):



#if __name__ == __main__:

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" diaslog box and return the path to the selected file

handle = KMLHandler(filename)