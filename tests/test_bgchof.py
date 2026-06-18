"""Simple tests using pytest.

- calculate Easter Sunday for 2021 (should return May 2nd, 2021)
- get the fasting status for a known Good Friday date (i.e. Apr 30 2021)


more complex tests




"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str((Path(__file__).parent.parent / "src").resolve()))
from bgchof import getStatusForDate


def test_bgchof_easter_2021_may2_is_6():
    """
    Test if status for known Easter Sunday is 6
    """
    assert getStatusForDate(date.fromisoformat("2021-05-02")) == 6


def test_st_peter_and_pauls_fast_year_2022():
    """
    # check St' Peter's Fast for year 2022 - should have a fast free week

    """
    start_date = date.fromisoformat("2022-06-13")
    end_date = date.fromisoformat("2022-06-19")
    delta = timedelta(days=1)
    status_array = []
    while start_date <= end_date:
        status_array.append(getStatusForDate(start_date))
        start_date += delta
    assert status_array == [6, 6, 6, 6, 6, 6, 6]

def test_status_sept_14_1976_equals_2():
    """
    check status for Sept. 14 - Day of the wholy cross - should be '2'
    """
    assert getStatusForDate(date.fromisoformat("1976-09-14")) == 2





# other tests
# test msg for locale 'en'


