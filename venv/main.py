# -*- coding: utf-8 -*-
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils.KMLHandler import KMLHandler

def chooseOpenFile():
    filepath = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
    filename = filepath.split(r'/')[-1]
    return filepath, filename

print("Bienvenu dans l'outil d'analyse de KML" )
print("Appuyez sur Entrée pour choisir un fichier KML")
start = input()
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filepath, filename = chooseOpenFile()

option =''
while option != 'q':
    option = ''
    print("Veuillez choisir parmis les options suivantes :\n"
          "1: Analyser le fichier : {0}\n"
          "2: Choisir un autre fichier\n"
          "3: Générer un KML augmenté\n"
          "4: Générer un CSV pour Camelia\n"
          "5: Générer un CSV avec toutes les données\n"
          "q: quitter\n".format(filename))
    option = input("choix :  ")

    if option == '1': # Analyser le fichier
        try:
            handle = KMLHandler(filepath)
        except Exception as e:
            print(e)
    elif option == '2': # Choisir un autre fichier
        filepath, filename = chooseOpenFile()
        handle = None
    elif option == '3': # Générer un KML augmenté
        try:
            handle.generateOutput()
            Tk().withdraw()
            output_filename = asksaveasfilename(defaultextension='.kml')
            f = open(output_filename, "w+")
            f.write(repr(handle))
            f.close()
        except Exception as e:
            print(e)
    elif option == '4': # Générer un CSV pour Camelia
        try:
            camelia = handle.camelia
            Tk().withdraw()
            output_filename = asksaveasfilename(defaultextension='.csv')
            camelia.to_csv(output_filename)
        except Exception as e:
            print(e)
    elif option == '5': # Générer un CSV avec toutes les données
        try:
            df = handle.outputdf
            output_filename = asksaveasfilename(defaultextension='.csv')
            df.to_csv(output_filename)
        except Exception as e:
            print(e)
