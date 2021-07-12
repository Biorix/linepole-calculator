from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils.KMLHandler import KMLHandler
from utils.KMLutils import separate_line, create_array_from_lines

import settings

def chooseOpenFile():
    filepath = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
    filename = filepath.split(r'/')[-1]
    return filepath, filename

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filepath, filename = chooseOpenFile()

settings.init()

handle = KMLHandler(filepath)
settings.space_by_type['custom'] = 10000000
handle.generatePoles()
df = handle.outputdf
lines = separate_line(df)
result = create_array_from_lines(lines)
"""
Le profil du numpy array "result" est le suivant :
+-----------+--------------+-----------+------------+----------+-----------+
| Line Name | Section Name | start Lat | start long | stop Lat | stop long |
|           |              |           |            |          |           |
+-----------+--------------+-----------+------------+----------+-----------+
|           |              |           |            |          |           |

"""

print(result)

