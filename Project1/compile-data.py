import os
import sys
import re
from geopy.distance import vincenty

workDirectory = ""

if os.path.isfile("Compiled Data/dataset1.csv"):
	print("Found the File!")
else:
	citiBikeDataDirectory = "Citi Bike Data"
	citiBikeDataFileNames = [
		"2013-07 - Citi Bike trip data - 1.csv",
		"2013-07 - Citi Bike trip data - 2.csv",
		"2013-08 - Citi Bike trip data - 1.csv",
		"2013-08 - Citi Bike trip data - 2.csv",
		"2013-09 - Citi Bike trip data - 1.csv",
		"2013-09 - Citi Bike trip data - 2.csv",
		"2013-10 - Citi Bike trip data - 1.csv",
		"2013-10 - Citi Bike trip data - 2.csv",
		"2013-11 - Citi Bike trip data - 1.csv",
		"2013-11 - Citi Bike trip data - 2.csv",
		"2013-12 - Citi Bike trip data.csv",
		"2014-01 - Citi Bike trip data.csv",
		"2014-02 - Citi Bike trip data.csv"
	]

	weatherDataFile = "Weather Data/NY305801_9255_edited.txt"

	citiBikeDataRaw = []

	for x in range(len(citiBikeDataFileNames)):
		filepath = citiBikeDataDirectory + "/" + citiBikeDataFileNames[x]
		with open(filepath) as f:
			lines = f.read().splitlines()
			lines.pop(0) #get rid of the first line that contains the column names
			for c in range(len(lines)):
				lines[c] = lines[c].replace('"','')
				lines[c] = lines[c].split(",")
				sLatLong = (lines[c][5], lines[c][6])
				eLatLong = (lines[c][9], lines[c][10])
				distance = vincenty(sLatLong, eLatLong).miles
				lines[c].extend([distance])
			citiBikeDataRaw.extend(lines)

	with open(weatherDataFile) as f:
		weatherDataRaw = f.read().splitlines()
		weatherDataRaw.pop(0) #again, get rid of the column names
		for c in range(len(weatherDataRaw)):
			weatherDataRaw[c] = weatherDataRaw[c].split(",")

	citiBikeData = []

	for i in range(len(citiBikeDataRaw)):
		instance = citiBikeDataRaw[i]
		date = citiBikeDataRaw[i][1].split(" ")[0].split("-") #uses the start date of the loan
		for j in range(len(weatherDataRaw)):
			if (date[0] == weatherDataRaw[j][4] and date[1] == weatherDataRaw[j][2] and date[2] == weatherDataRaw[j][0]):
				instance.extend([weatherDataRaw[j][5], weatherDataRaw[j][6], weatherDataRaw[j][7], weatherDataRaw[j][8], weatherDataRaw[j][9]])
				citiBikeData.append(instance)
				break

	#Final Columns:
	#  0 tripduration
	#  1 starttime
	#  2 stoptime
	#  3 start station id
	#  4 start station name
	#  5 start station latitude
	#  6 start station longitude
	#  7 end station id
	#  8 end station name
	#  9 end station latitude
	# 10 end station longitude
	# 11 bikeid
	# 12 usertype
	# 13 birth year
	# 14 gender
	# 15 start/end station distance
	# 16 PRCP
	# 17 SNOW
	# 18 TAVE
	# 19 TMAX
	# 20 TMIN
				
	maxLineCount = 250000
	lineCounter = 1
	fileCounter = 1
	outputDirectoryFilename = "Compiled Data/dataset"
	f = open(outputDirectoryFilename + str(fileCounter) + ".csv","w")
	for line in citiBikeData:
		if lineCounter == 250000:
			f.close()
			lineCounter = 1
			fileCounter = fileCounter + 1
			f = open(outputDirectoryFilename + str(fileCounter) + ".csv","w")
		f.write(",".join(map(str, line)) + "\n")
		lineCounter = lineCounter + 1