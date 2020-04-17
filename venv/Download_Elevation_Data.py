import os
latRange = [10,13]
lngRange = [-14,-12]
for lat in range(latRange[0], latRange[1]):
	for lng in range(lngRange[0], lngRange[1]):
		latSign = 'N'
		if lat < 0:
			latSign = 'S'
		lngSign = 'E'
		if lng < 0:
			lngSign = 'W'

		folder = latSign + str(abs(lat)).zfill(2)
		filename = folder + lngSign + str(abs(lng)).zfill(3)
		destination = r"D:\GuineaElevation" + folder + "\\" + filename + ".hgt.gz"
		source = "s3://elevation-tiles-prod/skadi/"+ folder +"/" + filename + ".hgt.gz"

		commands = ["aws s3 cp --no-sign-request", source, destination]
		process = os.system(' '.join(x for x in commands))

		[[11.447561, -12.672399], [11.446225, -12.672896]]