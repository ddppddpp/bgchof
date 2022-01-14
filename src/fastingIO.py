"""Serialize and deserialize a list of fasting values.

Uses .csv files in CFG_DATAFILE_PREFIX to read from and write into.
"""

# import generateCalendar
import csv
import sys, os

if "BGCHOF_CFG_CFG_DATAFILE_PREFIX" not in os.environ:
    BGCHOF_CFG_CFG_DATAFILE_PREFIX = "./.bgchofcache/"
else:
    BGCHOF_CFG_CFG_DATAFILE_PREFIX = os.environ["BGCHOF_CFG_CFG_DATAFILE_PREFIX"]
CFG_DATAFILE_MODE = 0o777


def readFastingList(inputYear):
    """Load contents of .csv cache file into a list.

    Args:
        inputYear: int representing the year for which to load the cache file.

    Returns:
        fastingList: a list of [int(0..365) dayNumber, int(0..6) statusValue].
    Raises:
        FileNotFoundError: if cache file doesn't exists. Moves on to create a new one.
    """
    fastingList = []
    fileName = BGCHOF_CFG_CFG_DATAFILE_PREFIX + str(inputYear) + ".csv"
    print("fileName=", fileName, "\n")
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
            + ". Creating new one...\n"
        )
        sys.stderr.write(msg)
        return None


def writeFastingList(inputYear, inputList):
    """Dump an year-worth of fasting statuses into a .csv cache file.

    Args:
        inputYear: an int representing the year for which the status values.
        inputList: a list of [int(0..365) dayNumber, int(0..6) statusValue]
    Returns:
        True: if serialization was successful.
    Raises:
        Returns error messages if cache directory exists or can't be created, if cache file can't be created.
    """
    # try to create the cache directory, write error to stdout if exists
    if not os.path.isdir(BGCHOF_CFG_CFG_DATAFILE_PREFIX):
        try:
            os.umask(0o022)
            os.makedirs(
                BGCHOF_CFG_CFG_DATAFILE_PREFIX, CFG_DATAFILE_MODE, exist_ok=True
            )
        except:
            sys.stderr.write("Can't create the cache directory.\n")
            exit(1)
    else:
        sys.stderr.write("Cache directory already exists.\n")
    fileName = BGCHOF_CFG_CFG_DATAFILE_PREFIX + str(inputYear) + ".csv"
    try:
        with open(fileName, mode="w") as fastingListFile:
            fileWriter = csv.writer(fastingListFile, delimiter=",")
            fileWriter.writerow(["dayNumber", "Status"])
            for n in range(len(inputList)):
                fileWriter.writerow([n + 1, inputList[n]])
        return True
    except:
        msg = "Can't create data file for year " + str(inputYear) + ".\n"
        sys.stderr.write(msg)
        exit(1)


# To do - add CLI arguments to manage cache, i.e. delete all .csv files
