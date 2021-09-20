from pprint import pprint
import json
import os
import datetime
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys

#Source: https://www.50states.com/abbreviations.htm
states_db = {
    'Alabama' : 'AL',
    'Alaska' : 'AK',
    'Arizona' : 'AZ',
    'Arkansas' : 'AR',
    'California' : 'CA',
    'Colorado' : 'CO',
    'Connecticut' : 'CT',
    'Delaware' : 'DE',
    'Florida' : 'FL',
    'Georgia' : 'GA',
    'Hawaii' : 'HI',
    'Idaho' : 'ID',
    'Illinois' : 'IL',
    'Indiana' : 'IN',
    'Iowa' : 'IA',
    'Kansas' : 'KS',
    'Kentucky' : 'KY',
    'Louisiana' : 'LA',
    'Maine' : 'ME',
    'Maryland' : 'MD',
    'Massachusetts' : 'MA',
    'Michigan' : 'MI',
    'Minnesota' : 'MN',
    'Mississippi' : 'MS',
    'Missouri' : 'MO',
    'Montana' : 'MT',
    'Nebraska' : 'NE',
    'Nevada' : 'NV',
    'New Hampshire' : 'NH',
    'New Jersey' : 'NJ',
    'New Mexico' : 'NM',
    'New York' : 'NY',
    'North Carolina' : 'NC',
    'North Dakota' : 'ND',
    'Ohio' : 'OH',
    'Oklahoma' : 'OK',
    'Oregon' : 'OR',
    'Pennsylvania' : 'PA',
    'Rhode Island' : 'RI',
    'South Carolina' : 'SC',
    'South Dakota' : 'SD',
    'Tennessee' : 'TN',
    'Texas' : 'TX',
    'Utah' : 'UT',
    'Vermont' : 'VT',
    'Virginia' : 'VA',
    'Washington' : 'WA',
    'West Virginia' : 'WV',
    'Wisconsin' : 'WI',
    'Wyoming' : 'WY',
    'District of Columbia' : 'DC',
    'United States of America' : 'USA'

}

def covid_predict(folder, state):

    for root, dirs, files in os.walk(F'/home/ajiang10224/mysite/{folder}'):
        for filename in files:
            if '.csv' in filename:
                myfile = open(os.path.join(F'/home/ajiang10224/mysite/{folder}', filename), "r")

    header = myfile.readline()
    data = myfile.readlines()
    myfile.close()
    stateCount = 0
    newDict = {}

    header = header.strip("\n").split(",")

    deaths_mean = -1
    deaths_lower = -1
    deaths_upper = -1
    location_name = -1
    date_ind = -1

    for i in range(len(header)):
        if 'deaths_mean' in header[i]:
            deaths_mean = i
        elif 'deaths_lower' in header[i]:
            deaths_lower = i
        elif 'deaths_upper' in header[i]:
            deaths_upper = i
        elif 'location_name' in header[i]:
            location_name = i
        elif 'date' in header[i]:
            date_ind = i

    for aline in data:
        pieces = aline.strip("\n").split(",")
        if state in pieces[location_name]:
            stateCount += 1
            date = pieces[date_ind].strip('"')
            dayNumber = datetime.datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday
            newDict[str(dayNumber)] = {'State': state, 'MeanDailyDeaths': pieces[deaths_mean], 'LowerBound': pieces[deaths_lower], 'UpperBound': pieces[deaths_upper]}
            continue
        elif state == 'United States of America':
            if 'US' in pieces[location_name]:
                stateCount += 1
                date = pieces[date_ind].strip('"')
                dayNumber = datetime.datetime.strptime(date, '%Y-%m-%d').timetuple().tm_yday
                newDict[str(dayNumber)] = {'State': state, 'MeanDailyDeaths': pieces[deaths_mean], 'LowerBound': pieces[deaths_lower], 'UpperBound': pieces[deaths_upper]}

    #print(json.dumps(newDict, indent = 4))
    #return ("Total number of entries: {}".format(stateCount))
    return newDict

def covid_actual(st):
    file = open("/home/ajiang10224/mysite/covid_deaths_usafacts.csv", "r")
    header = file.readline()
    data = file.readlines()
    file.close()

    header_pieces = header.strip("\n").split(",")

    newDict = {}

    for j in range(4, len(header_pieces)):
        if '/' in header_pieces[j][0:2]:
            dayNumber = datetime.datetime.strptime('0' + header_pieces[j], '%m/%d/%y').timetuple().tm_yday
        else:
            dayNumber = datetime.datetime.strptime(header_pieces[j], '%m/%d/%y').timetuple().tm_yday

        newDict[str(dayNumber)] = 0

        for aline in data:
            data_pieces = aline.strip("\n").split(",")
            if st == 'USA':
                for key, value in states_db.items():
                    if value in data_pieces[2]:
                        if dayNumber == 22:
                            newDict[str(dayNumber)] += int(data_pieces[j])

                        else:
                            newDict[str(dayNumber)] += int(data_pieces[j]) - int(data_pieces[j-1])
            else:
                if st in data_pieces[2]:
                    if dayNumber == 22:
                        newDict[str(dayNumber)] += int(data_pieces[j])

                    else:
                        newDict[str(dayNumber)] += int(data_pieces[j]) - int(data_pieces[j-1])

    #print(json.dumps(newDict, indent = 4))
    return newDict


#print(covid_predict("Georgia"))
#print(covid_actual("ga"))

def covid_writer(folder, state):
    predictDict = covid_predict(folder, state)
    actualDict = covid_actual(states_db[state])

    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'w+')

    compareFile.write("DayOfYear,ActualDeaths,EstimatedLow,EstimatedMean,Estimated High\n")

    for key, value in predictDict.items():
        if key in actualDict.keys():
            compareFile.write(F"{key},{actualDict[key]},{value['LowerBound']},{value['MeanDailyDeaths']},{value['UpperBound']}\n")

        else:
           compareFile.write(F"{key},N/A,{value['LowerBound']},{value['MeanDailyDeaths']},{value['UpperBound']}\n")

    compareFile.close()

def graph_maker_day(folder, state):
    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'r')

    header = compareFile.readline()
    data = compareFile.readlines()

    compareFile.close()

    for i in range(len(data)):
        data[i] = data[i].strip("\n").split(",")

    # data = np.array(data, dtype=float)

    #print(data)

    dayOfYear = []
    dayOfYearNoFuture = []
    actualDeaths = []
    actualDeathsNoNA = []
    estimatedLow = []
    estimatedMean = []
    estimatedHigh = []

    for x in data:
        dayOfYear.append(float(x[0]))
        actualDeaths.append(x[1])
        estimatedLow.append(float(x[2]))
        estimatedMean.append(float(x[3]))
        estimatedHigh.append(float(x[4]))

    for i in range(len(actualDeaths)):
        if 'N/A' not in actualDeaths[i]:
            actualDeathsNoNA.append(float(actualDeaths[i]))
            dayOfYearNoFuture.append(dayOfYear[i])

    #print(actualDeathsNoNA)

    matplotlib.use("Agg")

    for i in range(len(dayOfYear)):
        dayOfYear[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYear[i] - 1)
        dayOfYear[i] = dayOfYear[i].date()

    for i in range(len(dayOfYearNoFuture)):
        dayOfYearNoFuture[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYearNoFuture[i] - 1)
        dayOfYearNoFuture[i] = dayOfYearNoFuture[i].date()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    #plt.gca().xaxis.set_major_locator(mdates.DayLocator())

    plt.plot(dayOfYearNoFuture, actualDeathsNoNA, label='actual deaths')
    plt.plot(dayOfYear, estimatedMean, '--', label='estimated mean')
    plt.plot(dayOfYear, estimatedLow, '--', label='estimated low')
    plt.plot(dayOfYear, estimatedHigh, '--', label='estimated high')
    plt.legend()

    plt.xlabel("Date")
    plt.ylabel("Daily Deaths from COVID-19")

    plt.savefig(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future_daily.png')

    plt.close('all')

def graph_maker_week(folder, state):
    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'r')

    header = compareFile.readline()
    data = compareFile.readlines()

    compareFile.close()

    for i in range(len(data)):
        data[i] = data[i].strip("\n").split(",")

    dayOfYear = []
    dayOfYearNoFuture = []
    actualDeaths = []
    actualDeathsNoNA = []
    estimatedLow = []
    estimatedMean = []
    estimatedHigh = []

    weekOfYear = []
    weekOfYearNoFuture = []
    actualWeeklyDeaths = []
    estimatedWeeklyDeathsLow = []
    estimatedWeeklyDeathsMean = []
    estimatedWeeklyDeathsHigh = []

    #Stores data into lists
    for x in data:
        dayOfYear.append(int(x[0]))
        actualDeaths.append(x[1])
        estimatedLow.append(float(x[2]))
        estimatedMean.append(float(x[3]))
        estimatedHigh.append(float(x[4]))

    for i in range(len(actualDeaths)):
        if 'N/A' not in actualDeaths[i]:
            actualDeathsNoNA.append(int(actualDeaths[i]))
            dayOfYearNoFuture.append(int(dayOfYear[i]))

    for i in range(len(dayOfYear)):
        if dayOfYear[i] % 7 == 0:
            weekOfYear.append(dayOfYear[i]//7)
        elif i == len(dayOfYear) - 1:
            weekOfYear.append(dayOfYear[i]//7 + 1)

    for i in range(len(dayOfYearNoFuture)):
        if dayOfYearNoFuture[i] % 7 == 0:
            weekOfYearNoFuture.append(dayOfYearNoFuture[i]//7)
        elif i == len(dayOfYearNoFuture) - 1:
            weekOfYearNoFuture.append(dayOfYearNoFuture[i]//7 + 1)

    for i in range(len(weekOfYear)):
        weekOfYear[i] = 7*(weekOfYear[i]) - 6

    for i in range(len(weekOfYearNoFuture)):
        weekOfYearNoFuture[i] = 7*(weekOfYearNoFuture[i]) - 6

    lowWeekTotal = 0
    meanWeekTotal = 0
    highWeekTotal = 0
    for i in range(len(dayOfYear)):
        lowWeekTotal += estimatedLow[i]
        meanWeekTotal += estimatedMean[i]
        highWeekTotal += estimatedHigh[i]
        if dayOfYear[i] % 7 == 0 or i == len(dayOfYear) - 1:
            estimatedWeeklyDeathsLow.append(lowWeekTotal)
            estimatedWeeklyDeathsMean.append(meanWeekTotal)
            estimatedWeeklyDeathsHigh.append(highWeekTotal)
            lowWeekTotal = 0
            meanWeekTotal = 0
            highWeekTotal = 0

    weeklyActualTotal = 0
    for i in range(len(dayOfYearNoFuture)):
        weeklyActualTotal += actualDeathsNoNA[i]
        if dayOfYearNoFuture[i] % 7 == 0 or i == len(dayOfYearNoFuture) - 1:
            actualWeeklyDeaths.append(weeklyActualTotal)
            weeklyActualTotal = 0

    matplotlib.use("Agg")

    for i in range(len(weekOfYear)):
        weekOfYear[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(weekOfYear[i] - 1)
        weekOfYear[i] = weekOfYear[i].date()

    for i in range(len(weekOfYearNoFuture)):
        weekOfYearNoFuture[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(weekOfYearNoFuture[i] - 1)
        weekOfYearNoFuture[i] = weekOfYearNoFuture[i].date()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    #plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=35))

    plt.plot(weekOfYearNoFuture, actualWeeklyDeaths, label='actual deaths')
    plt.plot(weekOfYear, estimatedWeeklyDeathsMean, '--', label='estimated mean')
    plt.plot(weekOfYear, estimatedWeeklyDeathsLow, '--', label='estimated low')
    plt.plot(weekOfYear, estimatedWeeklyDeathsHigh, '--', label='estimated high')
    plt.legend()

    plt.xlabel("Date")
    plt.ylabel("Weekly Deaths from COVID-19")

    plt.savefig(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future_weekly.png')

    plt.close('all')

def graph_maker_five_day(folder, state):
    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'r')

    header = compareFile.readline()
    data = compareFile.readlines()

    compareFile.close()

    for i in range(len(data)):
        data[i] = data[i].strip("\n").split(",")

    # data = np.array(data, dtype=float)

    #print(data)

    dayOfYear = []
    dayOfYearNoFuture = []
    actualDeaths = []
    actualDeathsNoNA = []
    estimatedLow = []
    estimatedMean = []
    estimatedHigh = []

    for x in data:
        dayOfYear.append(float(x[0]))
        actualDeaths.append(x[1])
        estimatedLow.append(float(x[2]))
        estimatedMean.append(float(x[3]))
        estimatedHigh.append(float(x[4]))

    for i in range(len(actualDeaths)):
        if 'N/A' not in actualDeaths[i]:
            actualDeathsNoNA.append(float(actualDeaths[i]))
            dayOfYearNoFuture.append(dayOfYear[i])

    #print(actualDeathsNoNA)

    estimatedLowAvg = []
    estimatedMeanAvg = []
    estimatedHighAvg = []

    for i in range(len(dayOfYear)):
        count = i - 2
        tempLow = 0
        tempMean = 0
        tempHigh = 0
        for j in range(count, count + 5):
            if j < 0:
                tempLow += estimatedLow[0]
                tempMean += estimatedMean[0]
                tempHigh += estimatedHigh[0]

            elif j >= len(dayOfYear):
                tempLow += estimatedLow[-1]
                tempMean += estimatedMean[-1]
                tempHigh += estimatedHigh[-1]

            else:
                tempLow += estimatedLow[j]
                tempMean += estimatedMean[j]
                tempHigh += estimatedHigh[j]

        tempLow /= 5
        tempMean /= 5
        tempHigh /= 5

        estimatedLowAvg.append(tempLow)
        estimatedMeanAvg.append(tempMean)
        estimatedHighAvg.append(tempHigh)

    actualAvg = []

    for i in range(len(dayOfYearNoFuture)):
        count = i - 2
        tempActual = 0
        for j in range(count, count + 5):
            if j < 0:
                tempActual += actualDeathsNoNA[0]

            elif j >= len(dayOfYearNoFuture):
                tempActual += actualDeathsNoNA[-1]

            else:
                tempActual += actualDeathsNoNA[j]

        tempActual /= 5

        actualAvg.append(tempActual)

    matplotlib.use("Agg")

    for i in range(len(dayOfYear)):
        dayOfYear[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYear[i] - 1)
        dayOfYear[i] = dayOfYear[i].date()

    for i in range(len(dayOfYearNoFuture)):
        dayOfYearNoFuture[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYearNoFuture[i] - 1)
        dayOfYearNoFuture[i] = dayOfYearNoFuture[i].date()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.plot(dayOfYearNoFuture, actualAvg, label='actual deaths')
    plt.plot(dayOfYear, estimatedMeanAvg, '--', label='estimated mean')
    plt.plot(dayOfYear, estimatedLowAvg, '--', label='estimated low')
    plt.plot(dayOfYear, estimatedHighAvg, '--', label='estimated high')
    plt.legend()

    plt.xlabel("Date")
    plt.ylabel("Daily Deaths from COVID-19 (5 Day Average)")

    plt.savefig(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future_5_day_average.png')

    plt.close('all')

def graph_maker_seven_day(folder, state):
    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'r')

    header = compareFile.readline()
    data = compareFile.readlines()

    compareFile.close()

    for i in range(len(data)):
        data[i] = data[i].strip("\n").split(",")

    # data = np.array(data, dtype=float)

    #print(data)

    dayOfYear = []
    dayOfYearNoFuture = []
    actualDeaths = []
    actualDeathsNoNA = []
    estimatedLow = []
    estimatedMean = []
    estimatedHigh = []

    for x in data:
        dayOfYear.append(float(x[0]))
        actualDeaths.append(x[1])
        estimatedLow.append(float(x[2]))
        estimatedMean.append(float(x[3]))
        estimatedHigh.append(float(x[4]))

    for i in range(len(actualDeaths)):
        if 'N/A' not in actualDeaths[i]:
            actualDeathsNoNA.append(float(actualDeaths[i]))
            dayOfYearNoFuture.append(dayOfYear[i])

    #print(actualDeathsNoNA)

    estimatedLowAvg = []
    estimatedMeanAvg = []
    estimatedHighAvg = []

    for i in range(len(dayOfYear)):
        count = i - 3
        tempLow = 0
        tempMean = 0
        tempHigh = 0
        for j in range(count, count + 7):
            if j < 0:
                tempLow += estimatedLow[0]
                tempMean += estimatedMean[0]
                tempHigh += estimatedHigh[0]

            elif j >= len(dayOfYear):
                tempLow += estimatedLow[-1]
                tempMean += estimatedMean[-1]
                tempHigh += estimatedHigh[-1]

            else:
                tempLow += estimatedLow[j]
                tempMean += estimatedMean[j]
                tempHigh += estimatedHigh[j]

        tempLow /= 7
        tempMean /= 7
        tempHigh /= 7

        estimatedLowAvg.append(tempLow)
        estimatedMeanAvg.append(tempMean)
        estimatedHighAvg.append(tempHigh)

    actualAvg = []

    for i in range(len(dayOfYearNoFuture)):
        count = i - 3
        tempActual = 0
        for j in range(count, count + 7):
            if j < 0:
                tempActual += actualDeathsNoNA[0]

            elif j >= len(dayOfYearNoFuture):
                tempActual += actualDeathsNoNA[-1]

            else:
                tempActual += actualDeathsNoNA[j]

        tempActual /= 7

        actualAvg.append(tempActual)

    matplotlib.use("Agg")

    for i in range(len(dayOfYear)):
        dayOfYear[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYear[i] - 1)
        dayOfYear[i] = dayOfYear[i].date()

    for i in range(len(dayOfYearNoFuture)):
        dayOfYearNoFuture[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYearNoFuture[i] - 1)
        dayOfYearNoFuture[i] = dayOfYearNoFuture[i].date()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.plot(dayOfYearNoFuture, actualAvg, label='actual deaths')
    plt.plot(dayOfYear, estimatedMeanAvg, '--', label='estimated mean')
    plt.plot(dayOfYear, estimatedLowAvg, '--', label='estimated low')
    plt.plot(dayOfYear, estimatedHighAvg, '--', label='estimated high')
    plt.legend()

    plt.xlabel("Date")
    plt.ylabel("Daily Deaths from COVID-19 (7 Day Average)")

    plt.savefig(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future_7_day_average.png')

    plt.close('all')

def graph_maker_day_cumulative(folder, state):
    compareFile = open(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future.csv', 'r')

    header = compareFile.readline()
    data = compareFile.readlines()

    compareFile.close()

    for i in range(len(data)):
        data[i] = data[i].strip("\n").split(",")

    # data = np.array(data, dtype=float)

    #print(data)

    dayOfYear = []
    dayOfYearNoFuture = []
    actualDeaths = []
    actualDeathsNoNA = []
    estimatedLow = []
    estimatedMean = []
    estimatedHigh = []

    for x in data:
        dayOfYear.append(float(x[0]))
        actualDeaths.append(x[1])
        estimatedLow.append(float(x[2]))
        estimatedMean.append(float(x[3]))
        estimatedHigh.append(float(x[4]))

    for i in range(len(actualDeaths)):
        if 'N/A' not in actualDeaths[i]:
            actualDeathsNoNA.append(float(actualDeaths[i]))
            dayOfYearNoFuture.append(dayOfYear[i])

    estimatedSumLow = 0
    estimatedSumMean = 0
    estimatedSumHigh = 0
    for i in range(len(dayOfYear)):
        estimatedSumLow += estimatedLow[i]
        estimatedSumMean += estimatedMean[i]
        estimatedSumHigh += estimatedHigh[i]
        estimatedLow[i] = estimatedSumLow
        estimatedMean[i] = estimatedSumMean
        estimatedHigh[i] = estimatedSumHigh

    estimatedSumActual = 0
    for i in range(len(dayOfYearNoFuture)):
        estimatedSumActual += actualDeathsNoNA[i]
        actualDeathsNoNA[i] = estimatedSumActual

    matplotlib.use("Agg")

    for i in range(len(dayOfYear)):
        dayOfYear[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYear[i] - 1)
        dayOfYear[i] = dayOfYear[i].date()

    for i in range(len(dayOfYearNoFuture)):
        dayOfYearNoFuture[i] = datetime.datetime(2020, 1, 1) + datetime.timedelta(dayOfYearNoFuture[i] - 1)
        dayOfYearNoFuture[i] = dayOfYearNoFuture[i].date()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    plt.plot(dayOfYearNoFuture, actualDeathsNoNA, label='actual deaths')
    plt.plot(dayOfYear, estimatedMean, '--', label='estimated mean')
    plt.plot(dayOfYear, estimatedLow, '--', label='estimated low')
    plt.plot(dayOfYear, estimatedHigh, '--', label='estimated high')
    plt.legend()

    plt.xlabel("Date")
    plt.ylabel("Cumulative Daily Deaths from COVID-19")

    plt.tight_layout()
    plt.savefig(F'/home/ajiang10224/mysite/static/graphs/{folder}_{state}_with_future_daily_cumulative.png')

    plt.close('all')

#def main(argv=sys.argv):
#    args = argv
#    covid_writer(args[1], args[2])
#    graph_maker(args[1], args[2])

#if __name__ == '__main__':
#    main()
