# -*- coding: utf-8 -*-
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils.KMLHandler import KMLHandler
import settings
import traceback

def chooseOpenFile():
    filepath = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
    filename = filepath.split(r'/')[-1]
    return filepath, filename

print("Bienvenu dans l'outil d'analyse de KML" )

start = input("Appuyez sur Entrée pour choisir un fichier KML")
Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filepath, filename = chooseOpenFile()

option =''
analised = 'Non analysé'
while option != 'q':
    settings.init()
    option = ''
    print("Veuillez choisir parmis les options suivantes :\n"
          "1: Traiter le fichier : {0} ({1})\n"
          "2: Choisir un autre fichier\n"
          "3: Générer un KML augmenté\n"
          "4: Générer un CSV pour Camelia\n"
          "5: Générer un CSV avec toutes les données\n"
          "q: quitter\n".format(filename, analised))
    option = input("choix :  ")

    if option == '1': # Analyser le fichier
        try:
            handle = KMLHandler(filepath)
            analised = 'Analysé'
        except Exception as e:
            print(traceback.format_exc())
            print(e)

        suboption = ''
        while suboption != 'r':
            print("Veuillez choisir parmis les options suivantes :\n"
                  "1: Générer les positions des poteaux\n"
                  "2: Générer des lignes parallèles\n"
                  "r: retour\n")
            suboption = input("choix :  ")
            if suboption == '1':
                #pole generation
                custom_dist = None
                while custom_dist == None:
                    print("Pour préciser une distance particulière (>= 10) entre les poteaux, l'indiquer ici\n"
                          "Sinon appuyer sur entrée ou préciser '0'\n")
                    custom_dist = input("Distance : ")
                    if custom_dist != '' and custom_dist != '0':
                        if int(custom_dist) < 10:
                            print('La distance doit être supérieure ou égale à 10 m')
                            custom_dist = None
                        else:
                            settings.space_by_type['custom'] = int(custom_dist)
                try:
                    handle.generatePoles()
                    suboption = 'r'
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    suboption = 'r'

            elif suboption == '2':
                #parallel lines
                custom_offset = None
                while custom_offset == None:
                    offset = 2.0
                    print("Précisez une distance particulière entre les lignes parallèles (défaut 2.0 m)\n")
                    custom_offset = input("Distance : ")
                    if custom_offset != '' and custom_offset != '0':
                        custom_offset = float(custom_offset)
                        if not custom_offset >= 0:
                            print('La distance doit être un nombre')
                            custom_offset = None
                        else:
                            offset = custom_offset
                custom_dist_max = None
                while custom_dist_max == None:
                    max_dist = 6
                    print("Précisez une distance maximum entre la ligne centrale et la dernière ligne parallèle "
                          "(défaut 6.0 m)\n")
                    custom_dist_max = input("Distance : ")
                    if custom_dist_max != '' and custom_dist_max != '0':
                        custom_dist_max = float(custom_dist_max)
                        if not custom_dist_max >= 0:
                            print('La distance doit être un nombre')
                            custom_dist_max = None
                        else:
                            max_dist = custom_dist_max
                try:
                    handle.generateOffset(offset, max_dist)
                    suboption = 'r'
                except Exception as e:
                    print(traceback.format_exc())
                    print(e)
                    suboption = 'r'

    elif option == '2': # Choisir un autre fichier
        filepath, filename = chooseOpenFile()
        handle = None
        analised = 'Non analysé'
    elif option == '3': # Générer un KML augmenté
        try:
            handle.generateOutput()
            Tk().withdraw()
            output_filename = asksaveasfilename(defaultextension='.kml')
            f = open(output_filename, "w+")
            f.write(repr(handle))
            f.close()
        except Exception as e:
            print(traceback.format_exc())
            print(e)
    elif option == '4': # Générer un CSV pour Camelia
        try:
            camelia = handle.camelia
            Tk().withdraw()
            output_filename = asksaveasfilename(defaultextension='.csv')
            camelia.to_csv(output_filename)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
    elif option == '5': # Générer un CSV avec toutes les données
        try:
            df = handle.outputdf
            output_filename = asksaveasfilename(defaultextension='.csv')
            df.to_csv(output_filename)
        except Exception as e:
            print(traceback.format_exc())
            print(e)
