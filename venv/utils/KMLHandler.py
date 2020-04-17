
from utils.Mesures import get_elevation as get_alt, get_distance_with_altitude as get_dist, get_subcoord_dist as sub_dist
from pykml import parser
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

resolution = 25 #résolution pour déterminer l'altitude en metres
type = {'city':50, 'roads':100, 'hill':80, 'normal':100}

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


class LineSection:
    def __init__(self, coord1, coord2, typekey='normal'):
        """
        Object that represent a section of LineString between two coordinates
        :param coord1: tuple:(lat, long)
        :param coord2: tuple:(lat, long)
        :param type: str: 'city', 'roads', 'hill'
        """
        self.start, self.stop, self.type = coord1, coord2, typekey

    def _get_sliced_line(self):
        "Slice the section to get elevation every $resolution meter"
        return sub_dist(self.start, self.stop, type[self.type], unit='m')

    def _get_elevation(self):
        self.df = pd.DataFrame(self.sliced_line,columns=['lat','long'])
        coordList = []
        for i in range((self.df.shape[0])):
            # Using iloc to access the values of
            # the current row denoted by "i"
           coordList.append(list(self.df.iloc[i, :]))
        self.df['alt'] = get_alt(coordList)[0]

    

    sliced_line = property(_get_sliced_line)


if __name__ == "__main__":

    ls = LineSection((11.466135, -12.616524), ( 11.489022, -12.538672))
    print(ls._get_elevation())
    print('OK')

# Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
# filename = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
#
# handle = KMLHandler(filename)