"""Simple tests using pytest.

- calculate Easter Sunday for 2021 (should return May 2nd, 2021)
- get the fasting status for a known Good Friday date (i.e. Apr 30 2021)


more complex tests




"""
import pytest
from datetime import date

# from . import context
from src.bgchof import getStatusForDate


def test_bgchof_Easter_2021_May2_is_6():
    assert getStatusForDate(date.fromisoformat("2021-05-02")) == 6


# other tests

# test msg for locale 'en'