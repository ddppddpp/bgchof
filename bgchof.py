'''
Logic
the user asks for a particular date/week/month/year
- check if there is a file, matching the requested year
- if not, generate the full list for the year and write it down
- load the file and get the value for the requested period
- load the (localized) text strings matching the value(s)
- bassed on the request, form the output

- milestone 1 - cli output



'''
import sys
import fastingIO
import generateCalendar
import fastingStatus
from datetime import date
import sys


def getFastingStatusForDate(inputDate):
    #check if we have the list structure pre-populated
    myFastingList = fastingIO.readFastingList(inputDate.year)
    if myFastingList is None: # we found no file, we need to generate a list
        myFastingList = generateCalendar.fastingYearList(inputDate.year)
        #make sure we serialize the calendar, so it can be re-used in the future
        fastingIO.writeFastingList(inputDate.year,myFastingList)
        myFastingList = fastingIO.readFastingList(inputDate.year) #think how to avoid calling this twice
    #get the date number in the year
    dateNumber = generateCalendar.yearDayCurrYear(inputDate)
    return fastingStatus.fastingValue2Msg(int(myFastingList[dateNumber-1]))


def main(argv):
    #check for number of arguments - should be one (year) plus one (name of program itself)
    if (len(argv) > 2) or (len(argv) < 1):
        sys.stderr.write("USAGE: %s <date for which to get the orthodox fasting status> \n" % (argv[0])) 
        return None
    elif (len(argv) == 1):
        #sys.stderr.write("you provided no input\n")
        #return None
        dInputDate = date.today()
    else:
        sInputDate = argv[1]
         #check for valid type
        try:
            dInputDate = date.fromisoformat(sInputDate)
        except ValueError:
            sys.stderr.write("The argument should be an day in the format yyyy-mm-dd\n")
            return None
   
    #get the status
    resultStatus = getFastingStatusForDate(dInputDate)

    return resultStatus

if __name__ == "__main__":
    sys.exit(main(sys.argv)) 



#debug

#myDate = date.today()
#myDate = date(2022,11,11)
#status = getFastingStatusForDate(myDate)
#print(status)