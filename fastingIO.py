# serialize and deserialize a list of fasting values
import generateCalendar
import csv
import sys

def readFastingList(inputYear):
    fastingList = []
    fileName = str(inputYear) + '.csv'
    try:
        with open(fileName, mode='r') as fastingListFile:
            fileReader = csv.reader(fastingListFile, delimiter=',')
            next(fileReader, None) #skip headers --> should we validate instead?
            for row in fileReader:
                fastingList.append(row[1])
            return fastingList
    except FileNotFoundError as e:
        sys.stderr.write("Can't open the csv file.\n")
        return None
        



def writeFastingList(inputYear, inputList):
    fileName = str(inputYear) + '.csv'
    try:
        with open(fileName, mode='w') as fastingListFile:
            fileWriter = csv.writer(fastingListFile, delimiter=',')
            fileWriter.writerow(['dayNumber','Status'])
            for n in range(len(inputList)):
                fileWriter.writerow([n+1,inputList[n]])
        return True
    except:
        sys.stderr.write("Can't create a file %s.csv\n",str(inputYear))

def readFastingList2(inputYear):
    fastingList = []
    fileName = str(inputYear) + '.csv'


#debug - uncomment if needed
#myYear = 2021
#myList = generateCalendar.fastingYearList(myYear)
#writeFastingList(myYear,myList)
#myList = readFastingList(myYear)