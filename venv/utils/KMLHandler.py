from utils.Mesures import get_elevation as get_alt, get_distance_with_altitude as get_dist
from pykml import parser
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class KMLHandler:
    def __init__(self,kml_file):
        with open(kml_file) as kml:
            folder = parser.parse(kml).getroot().Document.Folder

        plnm = []
        cordi = []
        for pm in folder.Placemark:
            plnm1 = pm.name
            plcs1 = pm.LineString.coordinates
            plnm.append(plnm1.text)
            cordi.append(plcs1.text)

        self.db = pd.DataFrame()
        self.db['place_name'] = plnm
        self.db['coordinates'] = cordi
        self.db['Longitude'], db['Latitude'], db['value'] = zip(*db['coordinates'].apply(lambda x: x.split(',', 2)))

    def




#if __name__ == __main__:

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename() # show an "Open" diaslog box and return the path to the selected file

handle = KMLHandler(filename)