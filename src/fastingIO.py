# serialize and deserialize a list of fasting values
import generateCalendar
import csv
import sys, os

CFG_DATAFILE_PREFIX = "./.bgchofcache/"
CFG_DATAFILE_MODE = "0o666"


def readFastingList(inputYear):
    fastingList = []
    fileName = CFG_DATAFILE_PREFIX + str(inputYear) + ".csv"
    try:
        with open(fileName, mode="r") as fastingListFile:
            fileReader = csv.reader(fastingListFile, delimiter=",")
            next(fileReader, None)  # skip headers --> should we validate instead?
            for row in fileReader:
                fastingList.append(row[1])
            return fastingList
    except FileNotFoundError as e:
        msg = (
            "Can't find the data file for year "
            + str(inputYear)
            + ".Creating new one...\n"
        )
        sys.stderr.write(msg)
        return None


def writeFastingList(inputYear, inputList):
    # try to create the cache directory, write error to stdout if exists
    try:
        os.mkdir(CFG_DATAFILE_PREFIX, CFG_DATAFILE_MODE)
    except:
        sys.stderr.write("Cache directory already exists.\n")

    fileName = CFG_DATAFILE_PREFIX + str(inputYear) + ".csv"
    try:
        with open(fileName, mode="w") as fastingListFile:
            fileWriter = csv.writer(fastingListFile, delimiter=",")
            fileWriter.writerow(["dayNumber", "Status"])
            for n in range(len(inputList)):
                fileWriter.writerow([n + 1, inputList[n]])
        return True
    except:
        msg = "Can't create data file for year " + str(inputYear) + "\n"
        sys.stderr.write(msg)
        exit(1)


def readFastingList2(inputYear):
    fastingList = []
    fileName = str(inputYear) + ".csv"


# debug - uncomment if needed
# myYear = 2021
# myList = generateCalendar.fastingYearList(myYear)
# writeFastingList(myYear,myList)
# myList = readFastingList(myYear)
