"""Simple tests using pytest.

- calculate Easter Sunday for 2021 (should return May 2nd, 2021)
- get the fasting status for a known Good Friday date (i.e. Apr 30 2021)


more complex tests




"""
import pytest
import datetime
from datetime import date, datetime, timedelta
import sys, os

# from . import context

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from bgchof import getStatusForDate


def test_bgchof_Easter_2021_May2_is_6():
    assert getStatusForDate(date.fromisoformat("2021-05-02")) == 6


# check St' Peter's Fast for year 2022 - should have a fast free week
def test_st_peter_and_pauls_fast_year_2022():
    start_date = date.fromisoformat("2022-06-13")
    end_date = date.fromisoformat("2022-06-19")
    delta = timedelta(days=1)
    status_array = []
    while start_date <= end_date:
        status_array.append(getStatusForDate(start_date))
        start_date += delta
    assert status_array == [6, 6, 6, 6, 6, 6, 6]


# check status for Sept. 14 - Day of the wholy cross - should be '2'
def test_status_sept_14_1976_equals_2():
    assert getStatusForDate(date.fromisoformat("1976-09-14"))


# other tests

# test msg for locale 'en'
