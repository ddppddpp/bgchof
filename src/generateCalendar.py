"""A module that calculates the fasting status values for an year."""
import sys, os
from datetime import date, timedelta

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# from calculateEasterSunday import calcEaster
import calculateEasterSunday


def generateList(inputYear):
    """Create a list of 365 items and set a fasting status value of 6 to all to every one.

    Args:
        inputYear: int, representing the year for which to generate the list.
    Returns:
        fastingList: A list of 365 6's.
    Raises:
        ValueError: if the argument is not an int
    """
    fastingList = []
    if type(inputYear) is int:
        firstDay = date(inputYear, 1, 1)
        lastDay = date(inputYear, 12, 31)
        for n in range(int((lastDay - firstDay).days) + 1):
            fastingList.append(6)
        return fastingList
    else:
        raise ValueError("Please supply an int argument representing an year.")
        return None


def generateBaseFasting(inputYear, inputList):
    """Apply the basic fasting (i.e. non-holiday weekday) rules.

    General rules are - Wed and Fri - set status to 4.
    Exceptions - Jan 5, Aug 29, Sep 14.

    Args:
        inputYear: int, representing the year for which to generate the list.
        inputList: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fastingList: A list with applied base fasting rules.
    """
    # starting Jan 1st set the statuses for the base, 1-day fasting rules:
    firstDay = date(inputYear, 1, 1)
    lastDay = date(inputYear, 12, 31)
    # single day fasting

    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        # each wed, fri -  4 (fish)
        if (day.weekday() == 2) or (day.weekday() == 4):
            inputList[n] = 4
    # Jan 5 is the day before Holy Epiphany - 2 (no oil); if  on Sat or Sun -> 3 (plus oil)
    janFive = date(inputYear, 1, 5)
    if janFive.weekday() > 4:
        inputList[4] = 3
    else:
        inputList[4] = 2
    # Aug 29 - 2 (no oil) ; if  on Sat or Sun -> 3 (plus oil)
    augTwentyNine = date(inputYear, 8, 29)
    augTwentyNineYearDay = yearDayCurrYear(augTwentyNine)
    if augTwentyNine.weekday() > 4:
        inputList[augTwentyNineYearDay - 1] = 3
    else:
        inputList[augTwentyNineYearDay - 1] = 2
    # Sept 14 - 3 (hot food, cold food, plant based oil)
    septFourteen = date(inputYear, 9, 14)
    septFourteenYearDay = yearDayCurrYear(septFourteen)
    inputList[septFourteenYearDay - 1] = 2
    # <goodFri> - 0 - no food, no water
    # Easter Sunday calculation is expensive, try to do it once per calendar generation and then send it all procedures

    # return just the list as the calndar is global, is that ok?
    return inputList


def resurrectionFast(inputDate: date, inputList: list):
    """Apply fasting rules for the Resurrection (a.k.a. Easter) Fast.

    The resurreciton starts 7 weeks before Easter Sunday
    One week before that there's a fast-free (6) week of preparation (1st 7 days)
    0th week of the fast - all days - dairy/eggs (5)
    1st week - mon - sat 2, sun 3
    2nd week - check for Annunciation - March 25
    3nd through 5th week - mon-fri 2, sat-sun 3
    week 6 - mon-fri 2, sat - 3, sun 4 - Palm Sunday
    week 7 - mon-thu 2, fri - 6, sat 3, sun - Easter Sunday
    The week from Easter Sunday through Thomas Sunday is fast-free (6)

    Update:
    - according to Typikon, p.511-512 week, week 2 to 5 should be all status 3
    - first week should be 2 for Mon-Fri and 3 for the weekend

    Args:
        inputYear: int, representing the year for which to generate the list.
        inputList: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fastingList: A list with applied fasting status values for the Resurrection Fast.
    """
    firstDay = inputDate
    for n in range(1, 8):  # next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day) - 1] = 6
    firstDay = day
    for n in range(1, 8):  # next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day) - 1] = 5
    firstDay = day
    for n in range(1, 8):  # next 7 days
        day = firstDay + timedelta(days=n)
        if day.weekday() < 5:
            inputList[yearDayCurrYear(day) - 1] = 2
        else:
            inputList[yearDayCurrYear(day) - 1] = 3
    firstDay = day

    for n in range(1, 29):  # next 28 days
        day = firstDay + timedelta(days=n)
        # if day.weekday() < 5:
        #    inputList[yearDayCurrYear(day) - 1] = 2
        # else:
        inputList[yearDayCurrYear(day) - 1] = 3
    firstDay = day
    for n in range(1, 8):  # next seven days
        day = firstDay + timedelta(days=n)
        if day.weekday() < 6:
            inputList[yearDayCurrYear(day) - 1] = 3
        else:
            inputList[yearDayCurrYear(day) - 1] = 4
    firstDay = day
    for n in range(1, 8):  # next seven days
        day = firstDay + timedelta(days=n)
        if day.weekday() < 4:
            inputList[yearDayCurrYear(day) - 1] = 2
        elif day.weekday() == 4:
            inputList[yearDayCurrYear(day) - 1] = 0
        elif day.weekday() == 5:
            inputList[yearDayCurrYear(day) - 1] = 3
        else:
            inputList[yearDayCurrYear(day) - 1] = 6
    firstDay = day
    for n in range(1, 8):  # next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day) - 1] = 6

    # the Annunciation if celebrated on March 25 (fixed)
    # if this is not in the Holy Week, fish is allowed
    # check for Holy Week
    inputList[yearDayCurrYear(date(inputDate.year, 3, 25)) - 1] = 4

    return inputList


def stPeterAndPaulFast(pentecostDate: date, inputList: list):
    """Apply the fasting rules for St Peter and Paul's Fast.

    St Peter's Fasts start on the Monday after the 1st Sunday after Pentecost
    it ends on June 29th (fixed) - st Peter & Paul
    find the 1st sunday after pentecostDate

    TODO - check if there are 14 days b/w start and 29th.
    if yes - we need one 'fast free' week (status 6) before the fast starts

    Args:
        pentecostDate:  datetime.date, 50 days after Easter Sunday.
        inputList: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fastingList: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    if pentecostDate.weekday() == 6:
        firstDay = pentecostDate
    else:
        firstDay = pentecostDate
        while firstDay.weekday() < 7:
            firstDay += timedelta(days=1)
    # print('first sunday after penetecost',firstDay.strftime('%d-%m-%Y'))
    firstDay += timedelta(days=1)  # we actually start *after* the 1st sunday
    # lastDay is June 28 - the day before St. Peter and Paul's feast - fixed
    lastDay = date(pentecostDate.year, 6, 28)
    if date(pentecostDate.year, 6, 29) - pentecostDate > timedelta(days=14):
        # isert code for fast free week here
        for i in range(0, 7):
            day = firstDay + timedelta(days=i)
            inputList[yearDayCurrYear(day)] = 6
        # shift firsDay with one week
        firstDay = firstDay + timedelta(7)
        # go on with the stdandard rules -- THIS NEEDS HEAVT TESTS
        for n in range(int((lastDay - firstDay).days) + 1):
            day = firstDay + timedelta(days=n)
            if (day.weekday() == 2) or (day.weekday() == 4):
                inputList[yearDayCurrYear(day) - 1] = 3
            else:
                inputList[yearDayCurrYear(day) - 1] = 4
    else:
        for n in range(int((lastDay - firstDay).days) + 1):
            day = firstDay + timedelta(days=n)
            if (day.weekday() == 2) or (day.weekday() == 4):
                inputList[yearDayCurrYear(day) - 1] = 3
            else:
                inputList[yearDayCurrYear(day) - 1] = 4

    return inputList


def dormitionFast(inputYear, inputList):
    """Apply the fasting rules for the Dorminion Fast.

    The Dormition of the Mother of God is celebrated on Aug 15 as a fixed day
    The fasting starts on Aug 1 and ends on Aug 15. It is the 2nd most strict fast during the year
    Only cold food (1) is allowed on Mon, Wd, Fri
    On Tue, Thu - cooked food (2)
    Sat, Sun - oil and wine (3)
    The Transfiguration of Our Lord is celebrated on Aug 6, so fish is allowed on this day (4)
    If Aug 15 is on a Wed/Fri fish is allowed (4) <--- need to verify what to do on Sat/Sun Aug 15

    Args:
        inputYear:  int, the year for which to calculate the rules.
        inputList: a list of ints who's value will be modified to match the base fasting.
    Returns:
        inputList: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    firstDay = date(inputYear, 8, 1)
    lastDay = date(inputYear, 8, 15)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        if (day.weekday() == 0) or (day.weekday() == 2) or (day.weekday() == 4):
            inputList[dayNumber - 1] = 1
        elif (day.weekday() == 1) or (day.weekday() == 3):
            inputList[dayNumber - 1] = 2
        elif day.weekday() > 4:
            inputList[dayNumber - 1] = 3
    # Aug 6
    inputList[yearDayCurrYear(date(inputYear, 8, 6)) - 1] = 4
    # Aug 15
    if date(inputYear, 8, 15).weekday() == 2 or date(inputYear, 8, 15).weekday() == 4:
        inputList[yearDayCurrYear(date(inputYear, 8, 15)) - 1] = 4
    # All done - return the list
    return inputList


def nativityFast(inputYear, inputList):
    """Apply the fasting rules for the Nativity Fast.

    The Nativity Fast is on fixed dates each year
    It starts on Nov15 (a day after St Philip)
    Nov15 - Nov21 - Oil& Wine (3)
    Nov22 - Dec19 - Fish (4) if not Wed or Fri
    Dec20 - Dec24 - Oil & Wine (3)
    Dec25 - Jan4 - No fasting (meat - 6)

    Args:
        inputYear:  int, the year for which to calculate the rules.
        inputList: a list of ints who's value will be modified to match the base fasting.
    Returns:
        inputList: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    firstDay = date(inputYear, 11, 15)
    lastDay = date(inputYear, 11, 21)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber - 1] = 3
    firstDay = date(inputYear, 11, 22)
    lastDay = date(inputYear, 12, 19)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        if (day.weekday() != 2) and (day.weekday() != 4):
            inputList[dayNumber - 1] = 4
        else:
            inputList[dayNumber - 1] = 3
    firstDay = date(inputYear, 12, 20)
    lastDay = date(inputYear, 12, 24)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber - 1] = 3
    firstDay = date(inputYear, 12, 25)
    lastDay = date(inputYear, 12, 31)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber - 1] = 6
    firstDay = date(inputYear, 1, 1)
    lastDay = date(inputYear, 1, 4)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber - 1] = 6
    return inputList


def yearDayCurrYear(inputDate: date):
    """For a given date calculate the day number within the year.

    Args:
        inputDate: datetime.date for which to get the day number.

    Returns:
        day number - int (0..365/6)
    """
    return int(inputDate.toordinal() - date(inputDate.year, 1, 1).toordinal() + 1)


def _printCalendar(inputYear, inputList):
    # debugging purposes - print a list of dates and fasting status
    # example with similar iteration https://blog.finxter.com/iterating-through-a-range-of-dates-using-python-with-datetime/

    firstDay = date(inputYear, 1, 1)
    lastDay = date(inputYear, 12, 31)
    for n in range(int((lastDay - firstDay).days) + 1):
        day = firstDay + timedelta(days=n)
        # print(day.strftime('%d-%m-%Y'),',',day.weekday(),inputList[n])
        print(day.strftime("%d-%m-%Y"), ",", day.strftime("%a"), inputList[n])


def fastingYearList(inputYear):
    """Create a list and apply all rules in turn on it.

    Args:
        inputYear: integer - the year for which to do the calculations.
    Returns:
        fastingList: a list of integer 365 values (0..6)
    """
    fastingList = generateList(inputYear)
    generateBaseFasting(inputYear, fastingList)
    easterDate = calculateEasterSunday.calcEaster(inputYear)
    easterFastStartDate = easterDate - timedelta(days=63)
    resurrectionFast(easterFastStartDate, fastingList)
    pentecostDate = easterDate + timedelta(days=49)  # the 50th date after Easter Sunday
    stPeterAndPaulFast(pentecostDate, fastingList)
    dormitionFast(inputYear, fastingList)
    nativityFast(inputYear, fastingList)

    return fastingList


def getVeganDays(inputList):
    """Count the Vegan (no meat or animal based products allowed) days for a period.

    Args:
        inputList: a list of integers(0..6)
    Returns:
        veganDays: int - the number of items from the inputList with values less than 4.
    """
    veganDays = 0
    for n in range(len(inputList)):
        if int(inputList[n]) < 4:
            veganDays += 1
    return veganDays


def getVegetarianDays(inputList):
    """Count the Vegetarian (no meat, but poultry allowed) days for a period.

    Args:
        inputList: a list of integers(0..6)
    Returns:
        veganDays: int - the number of items from the inputList with values of 4 or 5.
    """
    vegetarianDays = 0
    for n in range(len(inputList)):
        if int(inputList[n]) > 3 and int(inputList[n]) < 6:
            vegetarianDays += 1
    return vegetarianDays


def main(argv):
    """Check the number of arguments and create a list with fasting status values.

    Args:
        yearNumber: int - the year for which to do calculations
    Returns:
        myList: a list of 365 integer values (0..6)
    Raises:
        valueError: if argument is not an int

    """
    if (len(argv) > 2) or (len(argv) < 2):
        sys.stderr.write(
            "USAGE: %s <year for which to generate a fasting caledndar in format YYYY> \n"
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
            "The argument should be an year for which to generate a fasting calendar\n"
        )
    # do some validation if needed
    # generate the lsit
    myList = fastingYearList(iInputYear)
    return myList


if __name__ == "__main__":
    sys.exit(main(sys.argv))
