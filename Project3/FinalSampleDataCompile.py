import os
from geopy.distance import vincenty
import holidays
from datetime import datetime
from dateutil.parser import parse
import glob
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

    ## Uncomment this line and modify path to project2 directory if you are running this script manually in a python console
#os.chdir(r"D:\Documents\School\SMU\2017 Spring\MSDS7331 - Data Mining\Projects\DataMining\Project2")

############################################################
# Load & Merge Data from Source Files
# Parse into Compiled Files
############################################################

starttime = datetime.now()
print('Starting Source Data Load & Merge Process. \n'
      'Start Time: ' + str(starttime))

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

                ## 1 = Yes
                ## 0 = No
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
            print(f)
            f.close()
            lineCounter = 1
            fileCounter = fileCounter + 1
            f = open(outputDirectoryFilename + str(fileCounter) + ".csv", "w")
        f.write(",".join(map(str, line)) + "\n")
        lineCounter = lineCounter + 1

    del citiBikeData

endtime = datetime.now()
print('Ending Source Data Load & Merge Process. \n'
      'End Time: ' + str(starttime) + '\n'
                                      'Total RunTime: ' + str(endtime - starttime))

############################################################
# Build & Parse Sampled Data INTO CSV FILES
############################################################
starttime = datetime.now()
print('\nStarting Build & Parse Sampled Data INTO CSV FILES Process. \n'
      'Start Time: ' + str(starttime))

if os.path.isfile("Final Sampled Data/SampleDataset1.csv"):
    print("Found the File!")
else:
    ############################################################
    # Load the Compiled Data from CSV
    ############################################################

    # Create CSV Reader Function and assign column headers
    def reader(f, columns):
        d = pd.read_csv(f)
        d.columns = columns
        return d


    # Identify All CSV FileNames needing to be loaded
    path = r'Compiled Data'
    all_files = glob.glob(os.path.join(path, "*.csv"))

    # Define File Columns
    columns = ["tripduration", "starttime", "stoptime", "start_station_id", "start_station_name",
               "start_station_latitude",
               "start_station_longitude", "end_station_id", "end_station_name", "end_station_latitude",
               "end_station_longitude", "bikeid", "usertype", "birth year", "gender", "LinearDistance", "DayOfWeek",
               "TimeOfDay", "HolidayFlag", "PRCP", "SNOW", "TAVE", "TMAX", "TMIN"]

    # Load Data
    CitiBikeDataCompiled = pd.concat([reader(f, columns) for f in all_files])

    # Replace '\N' Birth Years with Zero Values
    CitiBikeDataCompiled["birth year"] = CitiBikeDataCompiled["birth year"].replace(r'\N', '0')

    # Convert Columns to Numerical Values
    CitiBikeDataCompiled[['tripduration', 'birth year', 'LinearDistance', 'PRCP', 'SNOW', 'TAVE', 'TMAX', 'TMIN']] \
        = CitiBikeDataCompiled[['tripduration', 'birth year', 'LinearDistance', 'PRCP', 'SNOW', 'TAVE', 'TMAX',
                                'TMIN']].apply(pd.to_numeric)

    # Convert Columns to Date Values
    CitiBikeDataCompiled[['starttime', 'stoptime']] \
        = CitiBikeDataCompiled[['starttime', 'stoptime']].apply(pd.to_datetime)

    # Compute Age: 0 Birth Year = 0 Age ELSE Compute Start Time Year Minus Birth Year
    CitiBikeDataCompiled["Age"] = np.where(CitiBikeDataCompiled["birth year"] == 0, 0,
                                           CitiBikeDataCompiled["starttime"].dt.year - CitiBikeDataCompiled[
                                               "birth year"])

    # Convert Columns to Str Values
    CitiBikeDataCompiled[['start_station_id', 'end_station_id', 'bikeid', 'HolidayFlag', 'gender']] \
        = CitiBikeDataCompiled[['start_station_id', 'end_station_id', 'bikeid', 'HolidayFlag', 'gender']].astype(str)

    ############################################################
    # Remove Outliers
    ############################################################

    # Remove > 24 Hours
    CitiBikeDataCompiled = CitiBikeDataCompiled[CitiBikeDataCompiled["tripduration"] < 86400]

    # Log Transform Column Added
    CitiBikeDataCompiled["tripdurationLog"] = CitiBikeDataCompiled["tripduration"].apply(np.log)

    # Remove > 65 years old
    CitiBikeDataCompiled = CitiBikeDataCompiled[CitiBikeDataCompiled["Age"] <= 65]

    ############################################################
    # Sample to 500,000 Records
    ############################################################

    SampleSize = 500000

    CustomerSampleSize_Seed = int(round(SampleSize * 50.0 / 100.0, 0))
    SubscriberSampleSize_Seed = int(round(SampleSize * 50.0 / 100.0, 0))

    CitiBikeCustomerDataSampled = CitiBikeDataCompiled[CitiBikeDataCompiled["usertype"] == 'Customer'].sample(
        n=CustomerSampleSize_Seed, replace=False, random_state=CustomerSampleSize_Seed)

    CitiBikeSubscriberDataSampled = CitiBikeDataCompiled[CitiBikeDataCompiled["usertype"] == 'Subscriber'].sample(
        n=SubscriberSampleSize_Seed, replace=False, random_state=SubscriberSampleSize_Seed)

    CitiBikeDataSampled = pd.concat([CitiBikeCustomerDataSampled, CitiBikeSubscriberDataSampled])

    del CitiBikeDataCompiled

        ## Parse Sample Data into 2 Separate CSV Files (for GIT upload restrictions)
    CitiBikeDataSampled[:250000].to_csv('Final Sampled Data/SampleDataset1.csv', index=False)
    CitiBikeDataSampled[250000:].to_csv('Final Sampled Data/SampleDataset2.csv', index=False)

endtime = datetime.now()
print('Build & Parse Sampled Data INTO CSV FILES Process. \n'
      'End Time: ' + str(starttime) + '\n'
      'Total RunTime: ' + str(endtime - starttime))