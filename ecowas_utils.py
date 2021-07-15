from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from utils.KMLHandler import KMLHandler
from utils.KMLutils import create_array_from_info_df

import settings

def chooseOpenFile():
    filepath = askopenfilename() # show an "Open" diaslog box and return the path to the selected file
    filename = filepath.split(r'/')[-1]
    return filepath, filename

Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
filepath, filename = chooseOpenFile()


handle = KMLHandler(filepath)

result = create_array_from_info_df(handle.info_df)
"""
Le profil du numpy array "result" est le suivant :
+-----------+--------------+-----------+------------+----------+-----------+
| Line Name | Section Name | start Lat | start long | stop Lat | stop long |
|           |              |           |            |          |           |
+-----------+--------------+-----------+------------+----------+-----------+
|           |              |           |            |          |           |

"""

print(result)

