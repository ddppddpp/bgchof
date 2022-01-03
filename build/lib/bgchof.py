"""A python module to calculate a fasting diet.

Logic
the user asks for a particular date/week/month/year
- check if there is a file, matching the requested year
- if not, generate the full list for the year and write it down
- load the file and get the value for the requested period
- load the (localized) text strings matching the value(s)
- bassed on the request, form the output

"""
import sys, os
from datetime import date

# set sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastingIO import readFastingList, writeFastingList
from fastingStatus import fastingValue2Msg

# from calculateEasterSunday import calcEaster
from generateCalendar import fastingYearList, yearDayCurrYear


def getFastingMessageForDate(inputDate: date):
    """Calculate the fasting status and forms a text message for a particular date.

    Args:
        inputDate: a date for which to calculate the status

    Returns:
        An text string, describing the fasting do's and don'ts

    """
    # check if we have the list structure pre-populated
    myFastingList = readFastingList(inputDate.year)
    if myFastingList is None:  # we found no file, we need to generate a list
        myFastingList = fastingYearList(inputDate.year)
        # make sure we serialize the calendar, so it can be re-used in the future
        writeFastingList(inputDate.year, myFastingList)
        myFastingList = readFastingList(
            inputDate.year
        )  # think how to avoid calling this twice
    # get the date number in the year
    dateNumber = yearDayCurrYear(inputDate)
    return fastingValue2Msg(int(myFastingList[dateNumber - 1]))


def getStatusForDate(inputDate: date):
    """Calculate the fasting status for a particular date.

    Args:
        inputDate: a date for which to calculate the status

    Returns:
        An integer (0..6) representing the fasting status

    """
    # check if we have the list structure pre-populated
    myFastingList = readFastingList(inputDate.year)
    if myFastingList is None:  # we found no file, we need to generate a list
        myFastingList = fastingYearList(inputDate.year)
        # make sure we serialize the calendar, so it can be re-used in the future
        writeFastingList(inputDate.year, myFastingList)
        myFastingList = readFastingList(
            inputDate.year
        )  # think how to avoid calling this twice
    # get the date number in the year
    dateNumber = yearDayCurrYear(inputDate)
    return int(myFastingList[dateNumber - 1])


def main(argv):
    """Evaluate the CLI arguments and calculate the fasting status.

    Args:
        one argument: a date in YYYY-MM-DD format for which to calculate the status
        zero arguments/no input: defaults to the current date
        more than 1 argument: returns an error message
        anything else: raises a value error

    Returns:
        An integer (0..6) representing the fasting status

    """
    # check for number of arguments - should be one (year) plus one (name of program itself)
    if (len(argv) > 2) or (len(argv) < 1):
        sys.stderr.write(
            "USAGE: %s <date for which to get the orthodox fasting status> \n"
            % (argv[0])
        )
        return None
    elif len(argv) == 1:
        # sys.stderr.write("you provided no input\n")
        # return None
        dInputDate = date.today()
    else:
        sInputDate = argv[1]
        # check for valid type
        try:
            dInputDate = date.fromisoformat(sInputDate)
        except ValueError:
            sys.stderr.write("The argument should be an day in the format yyyy-mm-dd\n")
            return None

    # get the status
    resultStatus = getFastingMessageForDate(dInputDate)

    return resultStatus


if __name__ == "__main__":
    sys.exit(main(sys.argv))


# debug

# myDate = date.today()
# myDate = date(2024, 11, 11)
# status = getFastingStatusForDate(myDate)
# print(status)
