"""
Calculate the date for Easter Sunday
according to the Bulgarian Christian Orthodox Church Typikon
(1980 edition, p. 510-512).

For use in i.e. time shifting holidays and fasting
Easter Sunday should be the 1st Sunday after the first full moon after
the Spring Equinox
According to Bulgarian Christian Orthodox Typikon,
the date of Easter Sunday is found by dividing the year by 28 and by 19
and using lookup tables
The result should be b/w APR 4 and May 11 for the 20th and 21st centuries.
"""
import datetime
import sys
import warnings
from datetime import date, timedelta

from bgchof_settings import I_FIRST_VALID_YEAR, I_LAST_VALID_YEAR

# global constants
# Bulgaria implements the Gregorian calendar in 1916, valid dates are beyond 1917
# check here http://5ko.free.fr/bg/jul.php


def _calculate_month_and_line_number(input_year):
    """ Calculates the month for Easter Sunday
        and the line number in the Tipikon LUTs
    input_year"""
    # result
    month_and_line_number = []

    april_list_19 = [15, 4, 12, 1, 9, 17, 6, 14, 3, 11, 0, 8, 16, 5, 13, 2, 10]

    may_list_19 = [13, 2, 10, 18, 7]

    # edge cases: if ramainder is 13 or 2  or 10 it is a member of both
    # current implementation will asume April for all 3 edge cases

    remainder_19 = input_year % 19

    for i in april_list_19:
        if i == remainder_19:
            month_and_line_number.append(4)
            month_and_line_number.append(april_list_19.index(i))
            return month_and_line_number
    for j in may_list_19:
        if j == remainder_19:
            month_and_line_number.append(5)
            month_and_line_number.append(may_list_19.index(j))
            return month_and_line_number
    sys.stderr.write(
            f"You've just found an error in the Typikon LUTs for {input_year}\n"
        )
    return None


def calc_easter(input_year):
    """Calculate Easter Sunday based on look-up tables.

    Args:
        inputYear: an integer representing the year f
        or which to calculate EasterSunday
    Returns:
        result_ate: a datetime.date object
        representing Easter Sunday for inputYear.
    Raises
        ValueError: If inputYear is not set, not an int
        or not between I_LAST_VALID_YEARand I_FIRST_VALID_YEAR

    """
    if (
        not input_year
        or not isinstance(input_year, int)
        or input_year < I_FIRST_VALID_YEAR
        or input_year > I_LAST_VALID_YEAR
    ):

        raise ValueError(
            "The argument should be a valid year for which to calculate Easter Sunday"
        )
#        return None - check if you should call return after raising an exception

    # if valid
    else:
        result_year = int(input_year)
    #        try:
    #            result_year = int(input_year)
    #        except ValueError:
    #            sys.stderr.write(
    #                "The argument should be an year for which to calculate Easter Sunday\n"
    #            )
    #            return None
    # initialize result?
    result_month = 0
    result_day = 0
    match_column = ""
    result_ate = date.today()  # why?

    # set century constant compensation

    # lookup table definition
    april_dict_28 = {
        "II": [6, 6, 13, 13, 13, 13, 13, 20, 20, 20, 20, 27, 27, 27, 27, 27, 0],
        "III": [5, 5, 12, 12, 12, 12, 19, 19, 19, 19, 19, 26, 26, 26, 26, 0, 0],
        "IV": [4, 11, 11, 11, 11, 18, 18, 18, 18, 18, 25, 25, 25, 25, 0, 0, 0],
        "V": [10, 10, 10, 10, 10, 17, 17, 17, 17, 24, 24, 24, 24, 24, 0, 0, 0],
        "VI": [9, 9, 9, 9, 16, 16, 16, 16, 16, 23, 23, 23, 30, 30, 30, 30, 30],
        "VII": [8, 8, 8, 8, 15, 15, 15, 15, 22, 22, 22, 22, 29, 29, 29, 29, 29],
        "VIII": [7, 7, 7, 14, 14, 14, 14, 21, 21, 21, 21, 21, 28, 28, 28, 28, 0],
    }

    may_dict_28 = {
        "II": [0, 0, 4, 4, 4],
        "III": [0, 3, 3, 3, 3],
        "IV": [2, 2, 2, 2, 2],
        "V": [1, 1, 1, 1, 8],
        "VI": [0, 0, 0, 7, 7],
        "VII": [0, 0, 0, 6, 6],
        "VIII": [0, 0, 5, 5, 5],
    }

    # get the ramainders of division to 28 an to 19
    remainder_28 = input_year % 28

    # get the line number
    month_and_number = _calculate_month_and_line_number(input_year)

    result_month = month_and_number[0]
    # check which dict element we're in
    # II
    if remainder_28 in [9, 15, 20, 26]:
        match_column = "II"
    # III
    elif remainder_28 in [4, 10, 21, 27]:
        match_column = "III"
    # IV
    elif remainder_28 in [5, 11, 16, 22]:
        match_column = "IV"
    # V
    elif remainder_28 in [6, 17, 23, 0]:
        match_column = "V"
    # VI
    elif remainder_28 in [1, 7, 12, 18]:
        match_column = "VI"
    # VI
    elif remainder_28 in [2, 13, 19, 24]:
        match_column = "VII"
    # VIII
    elif remainder_28 in [3, 8, 14, 25]:
        match_column = "VIII"
    # III

    # now get the item matching colum and row; substract 1 from the row number,
    # to account for 0..n indexing
    if month_and_number[0] == 4:
        for k, v in april_dict_28.items():
            if k == match_column:
                # if len(v) <= month_and_number[1] or v[month_and_number[1]]==0:
                if v[month_and_number[1]] == 0:
                    # aparently this is the edge case so we're in May
                    month_and_number[0] = 5
                    month_and_number[1] -= 14
                    result_month = 5
                else:
                    result_day = v[month_and_number[1]]

    if month_and_number[0] == 5:
        for k, v in may_dict_28.items():
            if k == match_column:
                result_day = v[month_and_number[1]]

#    """
#    Correction for century
#    the look-up tables in the Tipikon are proven valid for
#                    1900-2099 where there are 13 day difference
#    between Old Style and New Style
#    dates before or after that should be corrected so that there are
#    5.10.1582 - 28.02.1700 - 10 days (-3 delta from the Tipikon)
#    29.02.1700 - 28.02.1800 - 11 days (-2 delta)
#    29.02.1800 - 28.02.1900 - 12 days (-1 delta)
#    2100 +   14 days (+1 delta)
#    more here http://5ko.free.fr/bg/jul.php
#    """

    # check if dates are b/w apr 4 and may 11
    result_ate = datetime.date(result_year, result_month, result_day)
    if result_year < 1700:
        century_time_delta=timedelta(days=3)
        result_ate = result_ate - century_time_delta
    elif result_year < 1800:
        century_time_delta=timedelta(days=2)
        result_ate = result_ate - century_time_delta
    elif result_year < 1900:
        century_time_delta=timedelta(days=1)
        result_ate = result_ate - century_time_delta
    elif result_year > 2099:
        century_time_delta=timedelta(days=1)
        result_ate = result_ate + century_time_delta
    return result_ate


# the check below is not valid for i.e. 1600, 1638, 1695 etc.
# it should probably be moved to tests anyway
#    try:
#        if (result_ate >= datetime.date(result_year,4,4))
#        and (result_ate <= datetime.date(result_year,5,11)):
#            return result_ate
#    except:
#        sys.stderr.write("Warning: Date should be between Apr 4 and May 11, something is wrong\n")
#        return None

def calcEaster(input_year):
    '''
    Legacy function - compatibility reasons
    use calc_easter() instead
    '''
    warnings.warn("calcEaster is being deprecated, pls use calc_easter().", stacklevel=2)
    return calc_easter(input_year)

def main(argv):
    """CLI interface to calculate Easter Sunday.

    Args:
        input_date: An integer argument in the YYYY format.
        Should be between I_FIRST_VALID_YEAR and I_LAST_VALID_YEAR.
        Mo arguments or more than one: Returns an error message.
        Non-int arument: Raises a ValueError.

    """
    # check for number of arguments -
    # should be one (year) plus one (name of program itself)
    if (len(argv) > 2) or (len(argv) < 2):
        error_string = f"USAGE: {argv[0]} <year for which to \
                        calculate Easter Sunday in format YYYY> \n"

        sys.stderr.write(error_string)
        return None

    s_input_year = argv[1]
    # check for valid type
    try:
        input_year = int(s_input_year)
    except ValueError:
        sys.stderr.write(
            "The argument should be an year for which to calculate Easter Sunday\n"
        )
        return None
    if (input_year < I_FIRST_VALID_YEAR) or (input_year > I_LAST_VALID_YEAR):
        sys.stderr.write("The requested year is not valid.\n")
        return None

    # find the date for Easter Sunday
    d_easter_sunday = calc_easter(input_year)
    # should we print or not?
    print(d_easter_sunday.strftime("%d-%m-%Y"))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
