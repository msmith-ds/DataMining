import os
import sys
import re
from geopy.distance import vincenty
import holidays
from datetime import datetime
from dateutil.parser import parse


starttime = datetime.now()
print(starttime)

if os.path.isfile("Compiled Data/dataset1.csv"):
    print("Found the File!")
else:
    citiBikeDataDirectory = "Citi Bike Data"
    citiBikeDataFileNames =[
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

    for file in citiBikeDataFileNames:
        print(file)
        filepath = citiBikeDataDirectory + "/" + file
        with open(filepath) as f:
            lines = f.read().splitlines()
            lines.pop(0)  # get rid of the first line that contains the column names
            for line in lines:
                line = line.replace('"', '')
                line = line.split(",")
                sLatLong = (line[5], line[6])
                eLatLong = (line[9], line[10])

                distance = vincenty(sLatLong, eLatLong).miles
                line.extend([distance])

                ## Monday       = 0
                ## Tuesday      = 1
                ## Wednesday    = 2
                ## Thursday     = 3
                ## Friday       = 4
                ## Saturday     = 5
                ## Sunday       = 6
                if parse(line[1]).weekday() == 0:
                    DayOfWeek = "Monday"
                elif parse(line[1]).weekday() == 1:
                    DayOfWeek = "Tuesday"
                elif parse(line[1]).weekday() == 2:
                    DayOfWeek = "Wednesday"
                elif parse(line[1]).weekday() == 3:
                    DayOfWeek = "Thursday"
                elif parse(line[1]).weekday() == 4:
                    DayOfWeek = "Friday"
                elif parse(line[1]).weekday() == 5:
                    DayOfWeek = "Saturday"
                else:
                    DayOfWeek = "Sunday"
                line.extend([DayOfWeek])

                ##Morning       5AM-10AM
                ##Midday        10AM-2PM
                ##Afternoon     2PM-5PM
                ##Evening       5PM-10PM
                ##Night         10PM-5AM

                if parse(line[1]).hour >= 5 and parse(line[1]).hour < 10:
                    TimeOfDay = 'Morning'
                elif parse(line[1]).hour >= 10 and parse(line[1]).hour < 14:
                    TimeOfDay = 'Midday'
                elif parse(line[1]).hour >= 14 and parse(line[1]).hour < 17:
                    TimeOfDay = 'Afternoon'
                elif parse(line[1]).hour >= 17 and parse(line[1]).hour < 22:
                    TimeOfDay = 'Evening'
                else:
                    TimeOfDay = 'Night'
                line.extend([TimeOfDay])


                if parse(line[1]) in holidays.UnitedStates():
                    holidayFlag = "1"
                else:
                    holidayFlag = "0"
                line.extend([holidayFlag])

                citiBikeDataRaw.append(line)
            del lines

    with open(weatherDataFile) as f:
        weatherDataRaw = f.read().splitlines()
        weatherDataRaw.pop(0)  # again, get rid of the column names
        for c in range(len(weatherDataRaw)):
            weatherDataRaw[c] = weatherDataRaw[c].split(",")
            # Adjust days and months to have a leading zero so we can capture all the data
            if len(weatherDataRaw[c][2]) < 2:
                weatherDataRaw[c][2] = "0" + weatherDataRaw[c][2]
            if len(weatherDataRaw[c][0]) < 2:
                weatherDataRaw[c][0] = "0" + weatherDataRaw[c][0]

    citiBikeData = []

    while (citiBikeDataRaw):
        instance = citiBikeDataRaw.pop()
        date = instance[1].split(" ")[0].split("-")  # uses the start date of the loan
        for record in weatherDataRaw:
            if (str(date[0]) == str(record[4]) and str(date[1]) == str(record[2]) and str(date[2]) == str(record[0])):
                instance.extend([record[5], record[6], record[7], record[8], record[9]])
                citiBikeData.append(instance)

    del citiBikeDataRaw
    del weatherDataRaw

    # Final Columns:
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
    # 16 DayOfWeek
    # 17 TimeOfDay
    # 18 HolidayFlag
    # 19 PRCP
    # 20 SNOW
    # 21 TAVE
    # 22 TMAX
    # 23 TMIN

    maxLineCount = 250000
    lineCounter = 1
    fileCounter = 1
    outputDirectoryFilename = "Compiled Data/dataset"
    f = open(outputDirectoryFilename + str(fileCounter) + ".csv", "w")
    for line in citiBikeData:
        if lineCounter == 250000:
            f.close()
            lineCounter = 1
            fileCounter = fileCounter + 1
            f = open(outputDirectoryFilename + str(fileCounter) + ".csv", "w")
        f.write(",".join(map(str, line)) + "\n")
        lineCounter = lineCounter + 1

endtime = datetime.now()
print("RunTime: ")
print(endtime-starttime)

