# -*- coding: utf-8 -*-
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils.KMLHandler import KMLHandler

# input = input("Appuyez sur Échap pour terminer ou Entrée pour traiter un autre fichier")
# while input != '\r' or input

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filename = askopenfilename()  # show an "Open" diaslog box and return the path to the selected file

handle = KMLHandler(filename)

# while input('Appuyer sur Entrée pour générer le kml') != '\r':
#     pass

handle.generateOutput()
print(handle)
output_filename = asksaveasfilename(defaultextension='.kml')
f = open(output_filename, "w+")
f.write(repr(handle))
f.close()
