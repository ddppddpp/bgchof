"""A module that calculates the fasting status values for an year."""
import sys
from datetime import date, timedelta

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
# from calculateEasterSunday import calcEaster
import calculateEasterSunday


def generate_list(input_year):
    """Create a list of 365 items and set a fasting status value of 6 to all to every one.

    Args:
        input_year: int, representing the year for which to generate the list.
    Returns:
        fasting_list: A list of 365 6's.
    Raises:
        ValueError: if the argument is not an int
    """
    fasting_list = []
    if isinstance(input_year, int):
        first_day = date(input_year, 1, 1)
        last_day = date(input_year, 12, 31)
        #for n in range(int((last_day - first_day).days) + 1):
        #   fasting_list.append(6)
        fasting_list = [6]* (int((last_day - first_day).days) + 1)
        return fasting_list
    else:
        raise ValueError("Please supply an int argument representing an year.")

def generateBaseFasting(input_year, input_list):
    """Apply the basic fasting (i.e. non-holiday weekday) rules.

    General rules are - Wed and Fri - set status to 4.
    Exceptions - Jan 5, Aug 29, Sep 14.

    Args:
        input_year: int, representing the year for which to generate the list.
        input_list: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fasting_list: A list with applied base fasting rules.
    """
    # starting Jan 1st set the statuses for the base, 1-day fasting rules:
    first_day = date(input_year, 1, 1)
    last_day = date(input_year, 12, 31)
    # single day fasting

    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        # each wed, fri -  4 (fish)
        if (day.weekday() == 2) or (day.weekday() == 4):
            input_list[n] = 4
    # Jan 5 is the day before Holy Epiphany - 2 (no oil); if  on Sat or Sun -> 3 (plus oil)
    jan_five = date(input_year, 1, 5)
    if jan_five.weekday() > 4:
        input_list[4] = 3
    else:
        input_list[4] = 2
    # Aug 29 - 2 (no oil) ; if  on Sat or Sun -> 3 (plus oil)
    aug_twenty_nine = date(input_year, 8, 29)
    aug_twenty_nine_year_day = date_number(aug_twenty_nine)
    if aug_twenty_nine.weekday() > 4:
        input_list[aug_twenty_nine_year_day - 1] = 3
    else:
        input_list[aug_twenty_nine_year_day - 1] = 2
    # Sept 14 - 3 (hot food, cold food, plant based oil)
    sept_fourteen = date(input_year, 9, 14)
    sept_fourteen_year_day = date_number(sept_fourteen)
    input_list[sept_fourteen_year_day - 1] = 2
    # <goodFri> - 0 - no food, no water
    # Easter Sunday calculation is expensive,
    #try to do it once per calendar generation and then send it all procedures

    # return just the list as the calndar is global, is that ok?
    return input_list


def resurrection_fast(input_date: date, input_list: list):
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
        input_year: int, representing the year for which to generate the list.
        input_list: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fasting_list: A list with applied fasting status values for the Resurrection Fast.
    """
    first_day = input_date
    for n in range(1, 8):  # next seven days
        day = first_day + timedelta(days=n)
        input_list[date_number(day) - 1] = 6
    first_day = day
    for n in range(1, 8):  # next seven days
        day = first_day + timedelta(days=n)
        input_list[date_number(day) - 1] = 5
    first_day = day
    for n in range(1, 8):  # next 7 days
        day = first_day + timedelta(days=n)
        if day.weekday() < 5:
            input_list[date_number(day) - 1] = 2
        else:
            input_list[date_number(day) - 1] = 3
    first_day = day

    for n in range(1, 29):  # next 28 days
        day = first_day + timedelta(days=n)
        # if day.weekday() < 5:
        #    input_list[date_number(day) - 1] = 2
        # else:
        input_list[date_number(day) - 1] = 3
    first_day = day
    for n in range(1, 8):  # next seven days
        day = first_day + timedelta(days=n)
        if day.weekday() < 6:
            input_list[date_number(day) - 1] = 3
        else:
            input_list[date_number(day) - 1] = 4
    first_day = day
    for n in range(1, 8):  # next seven days
        day = first_day + timedelta(days=n)
        if day.weekday() < 4:
            input_list[date_number(day) - 1] = 2
        elif day.weekday() == 4:
            input_list[date_number(day) - 1] = 0
        elif day.weekday() == 5:
            input_list[date_number(day) - 1] = 3
        else:
            input_list[date_number(day) - 1] = 6
    first_day = day
    for n in range(1, 8):  # next seven days
        day = first_day + timedelta(days=n)
        input_list[date_number(day) - 1] = 6

    # the Annunciation if celebrated on March 25 (fixed)
    # if this is not in the Holy Week, fish is allowed
    # check for Holy Week
    input_list[date_number(date(input_date.year, 3, 25)) - 1] = 4

    return input_list


def st_peter_and_paul_fast(pentecost_date: date, input_list: list):
    """Apply the fasting rules for St Peter and Paul's Fast.

    St Peter's Fasts start on the Monday after the 1st Sunday after Pentecost
    it ends on June 29th (fixed) - st Peter & Paul
    find the 1st sunday after pentecost_date
    If there are 14 days b/w start and 29th.
    there is one 'fast free' week (status 6) before the fast starts

    Args:
        pentecost_date:  datetime.date, 50 days after Easter Sunday.
        input_list: a list of ints who's value will be modified to match the base fasting.
    Returns:
        fasting_list: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    if pentecost_date.weekday() == 6:
        first_day = pentecost_date
    else:
        first_day = pentecost_date
        while first_day.weekday() != 6:
            first_day += timedelta(days=1)
    # print('first sunday after penetecost',first_day.strftime('%d-%m-%Y'))
    first_day += timedelta(days=1)  # we actually start *after* the 1st sunday
    # last_day is June 28 - the day before St. Peter and Paul's feast - fixed
    last_day = date(pentecost_date.year, 6, 28)
    if date(pentecost_date.year, 6, 29) - pentecost_date > timedelta(days=14):
        # isert code for fast free week here
        for i in range(0, 7):
            day = first_day + timedelta(days=i)
            input_list[date_number(day)] = 6
        # shift firsDay with one week
        first_day = first_day + timedelta(days=7)
        # go on with the stdandard rules -- THIS NEEDS HEAVT TESTS
        for n in range(int((last_day - first_day).days) + 1):
            day = first_day + timedelta(days=n)
            if (day.weekday() == 2) or (day.weekday() == 4):
                input_list[date_number(day) - 1] = 3
            else:
                input_list[date_number(day) - 1] = 4
    else:
        for n in range(int((last_day - first_day).days) + 1):
            day = first_day + timedelta(days=n)
            if (day.weekday() == 2) or (day.weekday() == 4):
                input_list[date_number(day) - 1] = 3
            else:
                input_list[date_number(day) - 1] = 4

    return input_list


def dormition_fast(input_year, input_list):
    """Apply the fasting rules for the Dorminion Fast.

    The Dormition of the Mother of God is celebrated on Aug 15 as a fixed day
    The fasting starts on Aug 1 and ends on Aug 15. It is the 2nd most strict fast during the year
    Only cold food (1) is allowed on Mon, Wd, Fri
    On Tue, Thu - cooked food (2)
    Sat, Sun - oil and wine (3)
    The Transfiguration of Our Lord is celebrated on Aug 6, so fish is allowed on this day (4)
    If Aug 15 is on a Wed/Fri fish is allowed (4) <--- need to verify what to do on Sat/Sun Aug 15

    Update & Simplification: According to the Tipykon, Aug 1 - Aug 14 should be status 3
    and for Aug 6 the status is 4.
    Aug 15 should be a non-fasting day (needs double checking)

    Args:
        input_year:  int, the year for which to calculate the rules.
        input_list: a list of ints who's value will be modified to match the base fasting.
    Returns:
        input_list: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    first_day = date(input_year, 8, 1)
    last_day = date(input_year, 8, 14)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        #    if (day.weekday() == 0) or (day.weekday() == 2) or (day.weekday() == 4):
        #        input_list[day_number - 1] = 1
        #    elif (day.weekday() == 1) or (day.weekday() == 3):
        #        input_list[day_number - 1] = 2
        #    elif day.weekday() > 4:
        input_list[day_number - 1] = 3
    # Aug 6
    input_list[date_number(date(input_year, 8, 6)) - 1] = 4
    # Aug 15
    # if date(input_year, 8, 15).weekday() == 2 or date(input_year, 8, 15).weekday() == 4:
    input_list[date_number(date(input_year, 8, 15)) - 1] = 6
    # All done - return the list
    return input_list


def nativity_fast(input_year, input_list):
    """Apply the fasting rules for the Nativity Fast.

    The Nativity Fast is on fixed dates each year
    It starts on Nov15 (a day after St Philip)
    Nov15 - Nov21 - Oil& Wine (3)
    Nov22 - Dec19 - Fish (4) if not Wed or Fri
    Dec20 - Dec24 - Oil & Wine (3)
    Dec25 - Jan4 - No fasting (meat - 6)

    Args:
        input_year:  int, the year for which to calculate the rules.
        input_list: a list of ints who's value will be modified to match the base fasting.
    Returns:
        input_list: A list with applied fasting status values for the St. Peter and Paul's Fast.
    """
    first_day = date(input_year, 11, 15)
    last_day = date(input_year, 11, 21)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        input_list[day_number - 1] = 3
    first_day = date(input_year, 11, 22)
    last_day = date(input_year, 12, 19)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        if (day.weekday() != 2) and (day.weekday() != 4):
            input_list[day_number - 1] = 4
        else:
            input_list[day_number - 1] = 3
    first_day = date(input_year, 12, 20)
    last_day = date(input_year, 12, 24)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        input_list[day_number - 1] = 3
    first_day = date(input_year, 12, 25)
    last_day = date(input_year, 12, 31)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        input_list[day_number - 1] = 6
    first_day = date(input_year, 1, 1)
    last_day = date(input_year, 1, 4)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        day_number = date_number(day)
        input_list[day_number - 1] = 6
    return input_list


def date_number(input_date: date):
    """For a given date calculate the day number within the year.

    Args:
        input_date: datetime.date for which to get the day number.

    Returns:
        day number - int (0..365/6)
    """
    return int(input_date.toordinal() - date(input_date.year, 1, 1).toordinal() + 1)


def _print_calendar(input_year, input_list):
    """
    # debugging purposes - print a list of dates and fasting status
    # example with similar iteration
    # https://blog.finxter.com/iterating-through-a-range-of-dates-using-python-with-datetime/
    """
    first_day = date(input_year, 1, 1)
    last_day = date(input_year, 12, 31)
    for n in range(int((last_day - first_day).days) + 1):
        day = first_day + timedelta(days=n)
        # print(day.strftime('%d-%m-%Y'),',',day.weekday(),input_list[n])
        print(day.strftime("%d-%m-%Y"), ",", day.strftime("%a"), input_list[n])


def fastingYearList(input_year):
    """Create a list and apply all rules in turn on it.

    Args:
        input_year: integer - the year for which to do the calculations.
    Returns:
        fasting_list: a list of integer 365 values (0..6)
    """
    fasting_list = generate_list(input_year)
    generateBaseFasting(input_year, fasting_list)
    easter_date = calculateEasterSunday.calcEaster(input_year)
    easter_fast_start_date = easter_date - timedelta(days=63)
    resurrection_fast(easter_fast_start_date, fasting_list)
    pentecost_date = easter_date + timedelta(days=49)  # the 50th date after Easter Sunday
    st_peter_and_paul_fast(pentecost_date, fasting_list)
    dormition_fast(input_year, fasting_list)
    nativity_fast(input_year, fasting_list)

    return fasting_list


def get_vegan_days(input_list):
    """Count the Vegan (no meat or animal based products allowed) days for a period.

    Args:
        input_list: a list of integers(0..6)
    Returns:
        vegan_dayss: int - the number of items from the input_list with values less than 4.
    """
    return sum(1 for status in input_list if status < 4)

def get_vegetarian_days(input_list):
    """Count the Vegetarian (no meat, but poultry allowed) days for a period.

    Args:
        input_list: a list of integers(0..6)
    Returns:
        vegan_days: int - the number of items from the input_list with values of 4 or 5.
    """
    return sum(1 for status in input_list if 3 < status < 6)


def main(argv):
    """Check the number of arguments and create a list with fasting status values.

    Args:
        yearNumber: int - the year for which to do calculations
    Returns:
        my_list: a list of 365 integer values (0..6)
    Raises:
        valueError: if argument is not an int

    """
    if (len(argv) > 2) or (len(argv) < 2):
        sys.stderr.write(f"USAGE:{argv[0]} <year for which to generate \
                        a fasting caledndar in format YYYY> \n")
        return None
    else:
        s_input_year = argv[1]
    # check for valid type
    try:
        i_input_year = int(s_input_year)
    except ValueError:
        sys.stderr.write(
            "The argument should be an year \
                for which to generate a fasting calendar\n"
        )
    # do some validation if needed
    # generate the list
    return fastingYearList(i_input_year)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
