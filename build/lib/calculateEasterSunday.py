"""Calculate the date for Easter Sunday according to the Bulgarian Christian Orthodox Church Typikon (1980 edition, p. 510-512).

For use in i.e. time shifting holidays and fasting
Easter Sunday should be the 1st Sunday after the first full moon after the Spring Equinox
According to Bulgarian Christian Orthodox Typikon,
the date of Easter Sunday is found by dividing the year by 28 and by 19 and using lookup tables
The result should be b/w APR 4 and May 11 for the 20th and 21st centuries.
"""
import datetime
from datetime import date
import sys

# global constants
iFIRSTVALIDYEAR = 1582
iLASTVALIDYEAR = 9999
# Bulgaria implements the Gregorian calendar in 1916, valid dates are beyond 1917
# check here http://5ko.free.fr/bg/jul.php


def _calculateMonthAndLineNumber(inputYear):

    # result
    monthAndLineNumber = []

    aprilList19 = [15, 4, 12, 1, 9, 17, 6, 14, 3, 11, 0, 8, 16, 5, 13, 2, 10]

    mayList19 = [13, 2, 10, 18, 7]

    # edge case: if ramainder is 13 or 2 it is a member of both

    remainder19 = inputYear % 19

    for i in aprilList19:
        if i == remainder19:
            monthAndLineNumber.append(4)
            monthAndLineNumber.append(aprilList19.index(i))
            return monthAndLineNumber
    for j in mayList19:
        if j == remainder19:
            monthAndLineNumber.append(5)
            monthAndLineNumber.append(mayList19.index(j))
            return monthAndLineNumber


def calcEaster(inputYear):
    """Calculate Easter Sunday based on look-up tables.

    Args:
        inputYear: an integer representing the year for which to calculate EasterSunday
    Returns:
        resultDate: a datetime.date object representing Easter Sunday for inputYear.
    Raises
        ValueError: If inputYear is not set, not an int or not between iLASTVALIDYEARand iFIRSTVALIDYEAR

    """
    if (
        not inputYear
        or not isinstance(inputYear, int)
        or inputYear < iFIRSTVALIDYEAR
        or inputYear > iLASTVALIDYEAR
    ):

        raise ValueError(
            "The argument should be a valid year for which to calculate Easter Sunday"
        )
        return None

    # if valid
    else:
        resultYear = int(inputYear)
    #        try:
    #            resultYear = int(inputYear)
    #        except ValueError:
    #            sys.stderr.write(
    #                "The argument should be an year for which to calculate Easter Sunday\n"
    #            )
    #            return None
    # initialize result?
    resultMonth = 0
    resultDay = 0
    matchColumn = ""
    resultDate = date.today()  # why?

    # set century constant compensation

    # lookup table definition
    aprilDict28 = {
        "II": [6, 6, 13, 13, 13, 13, 13, 20, 20, 20, 20, 27, 27, 27, 27, 27, 0],
        "III": [5, 5, 12, 12, 12, 12, 19, 19, 19, 19, 19, 26, 26, 26, 26, 0, 0],
        "IV": [4, 11, 11, 11, 11, 18, 18, 18, 18, 18, 25, 25, 25, 25, 0, 0, 0],
        "V": [10, 10, 10, 10, 10, 17, 17, 17, 17, 24, 24, 24, 24, 24, 0, 0, 0],
        "VI": [9, 9, 9, 9, 16, 16, 16, 16, 16, 23, 23, 23, 30, 30, 30, 30, 30],
        "VII": [8, 8, 8, 8, 15, 15, 15, 15, 22, 22, 22, 22, 29, 29, 29, 29, 29],
        "VIII": [7, 7, 7, 14, 14, 14, 14, 21, 21, 21, 21, 21, 28, 28, 28, 28, 0],
    }

    mayDict28 = {
        "II": [0, 0, 4, 4, 4],
        "III": [0, 3, 3, 3, 3],
        "IV": [2, 2, 2, 2, 2],
        "V": [1, 1, 1, 1, 8],
        "VI": [0, 0, 0, 7, 7],
        "VII": [0, 0, 0, 6, 6],
        "VIII": [0, 0, 5, 5, 5],
    }

    # get the ramainders of division to 28 an to 19
    remainder28 = inputYear % 28
    remainder19 = inputYear % 19

    # get the line number
    monthAndNumber = _calculateMonthAndLineNumber(inputYear)

    resultMonth = monthAndNumber[0]
    # check which dict element we're in
    # II
    if remainder28 in [9, 15, 20, 26]:
        matchColumn = "II"
    # III
    elif remainder28 in [4, 10, 21, 27]:
        matchColumn = "III"
    # IV
    elif remainder28 in [5, 11, 16, 22]:
        matchColumn = "IV"
    # V
    elif remainder28 in [6, 17, 23, 0]:
        matchColumn = "V"
    # VI
    elif remainder28 in [1, 7, 12, 18]:
        matchColumn = "VI"
    # VI
    elif remainder28 in [2, 13, 19, 24]:
        matchColumn = "VII"
    # VIII
    elif remainder28 in [3, 8, 14, 25]:
        matchColumn = "VIII"
    # III

    # now get the item matching colum and row; substract 1 from the row number, to account for 0..n indexing
    if monthAndNumber[0] == 4:
        for k, v in aprilDict28.items():
            if k == matchColumn:
                # if len(v) <= monthAndNumber[1] or v[monthAndNumber[1]]==0:
                if v[monthAndNumber[1]] == 0:
                    # aparently this is the edge case so we're in May
                    monthAndNumber[0] = 5
                    monthAndNumber[1] -= 14
                    resultMonth = 5
                else:
                    resultDay = v[monthAndNumber[1]]

    if monthAndNumber[0] == 5:
        for k, v in mayDict28.items():
            if k == matchColumn:
                resultDay = v[monthAndNumber[1]]

    """Correction for century
    the look-up tables in the Tipikon are proven valid for 1900-2099 where there are 13 day difference
    between Old Style and New Style
    dates before or after that should be corrected so that there are
    5.10.1582 - 28.02.1700 - 10 days (-3 delta from the Tipikon)
    29.02.1700 - 28.02.1800 - 11 days (-2 delta)
    29.02.1800 - 28.02.1900 - 12 days (-1 delta)
    2100 +   14 days (+1 delta)
    more here http://5ko.free.fr/bg/jul.php
    """
    if resultYear < 1700:
        resultDay -= 3
    elif resultYear < 1800:
        resultDay -= 2
    elif resultYear < 1900:
        resultDay -= 1
    elif resultYear > 2099:
        resultDay += 1

    # check if dates are b/w apr 4 and may 11
    resultDate = datetime.date(resultYear, resultMonth, resultDay)
    return resultDate


# the check below is not valid for i.e. 1600, 1638, 1695 etc.
# it should probably be moved to tests anyway
#    try:
#        if (resultDate >= datetime.date(resultYear,4,4)) and (resultDate <= datetime.date(resultYear,5,11)):
#            return resultDate
#    except:
#        sys.stderr.write("Warning: Date should be between Apr 4 and May 11, something is wrong\n")
#        return None


def main(argv):
    """CLI interface to calculate Easter Sunday.

    Args:
        inputDate: An integer argument in the YYYY format. Should be between iFIRSTVALIDYEAR and iLASTVALIDYEAR.
        no arguments or more than one: Returns an error message.
        Non-int arument: Raises a ValueError.

    """
    # check for number of arguments - should be one (year) plus one (name of program itself)
    if (len(argv) > 2) or (len(argv) < 2):
        sys.stderr.write(
            "USAGE: %s <year for which to calculate Easter Sunday in format YYYY> \n"
            % (argv[0])
        )
        return None
    else:
        sInputYear = argv[1]
    # check for valid type
    try:
        iInputYear = int(sInputYear)
    except ValueError:
        sys.stderr.write(
            "The argument should be an year for which to calculate Easter Sunday\n"
        )
        return None
    if (iInputYear < iFIRSTVALIDYEAR) or (iInputYear > iLASTVALIDYEAR):
        sys.stderr.write("The requested year is not valid.\n")
        return None

    # find the date fo Easter Sunday
    dEasterSunday = calcEaster(iInputYear)
    # should we print or not?
    print(dEasterSunday.strftime("%d-%m-%Y"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
