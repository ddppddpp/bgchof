''' Test cases for Easter Calculation'''
import datetime
import sys
from pathlib import Path

import pytest
from src import calculateEasterSunday as calculateEaster

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))


class TestEaster:
    """A class to test Easter dates"""

    def test_pe_1983(self):
        """20th century example from the Tipikon"""
        assert calculateEaster.calcEaster(1983) == datetime.date(1983, 5, 8)

    def test_pe_1995(self):
        """20th century example two from the Tipikon"""
        assert calculateEaster.calcEaster(1995) == datetime.date(1995, 4, 23)

    def test_easter_2021(self):
        """21st century example two"""
        assert calculateEaster.calcEaster(2021) == datetime.date(2021, 5, 2)

    # test for leap year - known leap - i.e. 2012, 2020,
    #also edge cases - 100s(non leap) and 400s(leap)
    # important tests for leap years are 1600, 2000 (leap)
    # and 1700, 1800, 1900, 2100
    # edge cases - Apr24 - 30, May 1-7 - those dates are on the border
    # b/w Apr and May in the Tipikon LuTs,
    # any errors in the calculations should fall there
    def test_easter_1600(self):
        """
        Leap year 1600 (divisible by 100 but also divisible by 400)
        Note - no Revised Julian for this date
        """
        assert calculateEaster.calcEaster(1600) == datetime.date(1600, 4, 2)


    def test_easter_1700(self):
        """
        Non-leap year 1700 (divisible by 100)
        Note - no Revised Julian for this date
        """
        assert calculateEaster.calcEaster(1700) == datetime.date(1700, 4, 11)

    def test_easter_1800(self):
        """Non-leap year 1700 (divisible by 100)  Note - no Revised Julian for this date"""
        assert calculateEaster.calcEaster(1800) == datetime.date(1800, 4, 20)

    def test_easter_1900(self):
        """Non-leap year 1900 (divisible by 100)  Note - no Revised Julian for this date"""
        assert calculateEaster.calcEaster(1900) == datetime.date(1900, 4, 22)

    def test_easter_2000(self):
        """Leap year 2000 (divisible by 100 but also divisible by 400)"""
        assert calculateEaster.calcEaster(2000) == datetime.date(2000, 4, 30)

    def test_easter_2100(self):
        """22th century example"""
        assert calculateEaster.calcEaster(2100) == datetime.date(2100, 5, 2)

    def test_easter_empty_string(self):
        """# test for empty string"""
        with pytest.raises(
            ValueError,
            match="The argument should be a valid year for which to calculate Easter Sunday",
        ):
            calculateEaster.calcEaster("")

# important tests for leap years are 1600, 2000 (leap) and 1700, 1800, 1900, 2100
# edge cases - Apr24 - 30, May 1-7 - those dates are on the border
# b/w Apr and May in the Tipikon LuTs,

    def test_easter_2016(self):
        """Test Easter for 2016 - 01.05"""
        assert calculateEaster.calcEaster(2016) == datetime.date(2016, 5, 1)

    def test_easter_2027(self):
        """2027 - 02.05"""
        assert calculateEaster.calcEaster(2027) == datetime.date(2027, 5, 2)

    def test_easter_2054(self):
        """2054 - 03.05"""
        assert calculateEaster.calcEaster(2054) == datetime.date(2054, 5, 3)

    def test_easter_2059(self):
        """2059 - 04.05"""
        assert calculateEaster.calcEaster(2059) == datetime.date(2059, 5, 4)

    def test_easter_2013(self):
        """2013 - 05.05"""
        assert calculateEaster.calcEaster(2013) == datetime.date(2013, 5, 5)

    def test_easter_2040(self):
        """2040 - 06.05"""
        assert calculateEaster.calcEaster(2040) == datetime.date(2040, 5, 6)

    def test_easter_2051(self):
        """2051 - 07.05"""
        assert calculateEaster.calcEaster(2051) == datetime.date(2051, 5, 7)

    def test_easter_2062(self):
        """2062 - 30.04"""
        assert calculateEaster.calcEaster(2062) == datetime.date(2062, 4, 30)

    def test_easter_2057(self):
        """2057 - 29.04"""
        assert calculateEaster.calcEaster(2057) == datetime.date(2057, 4, 29)

    def test_easter_2019(self):
        """2019 - 28.04"""
        assert calculateEaster.calcEaster(2019) == datetime.date(2019, 4, 28)

    def test_easter_2087(self):
        """2087 - 27.04"""
        assert calculateEaster.calcEaster(2087) == datetime.date(2087, 4, 27)

    def test_easter_2065(self):
        """2065 - 26.04"""
        assert calculateEaster.calcEaster(2065) == datetime.date(2065, 4, 26)

    def test_easter_2060(self):
        """2060 - 25.04"""
        assert calculateEaster.calcEaster(2060) == datetime.date(2060, 4, 25)

    def test_easter_2022(self):
        """2022 - 24.04"""
        assert calculateEaster.calcEaster(2022) == datetime.date(2022, 4, 24)

    def test_easter_1905(self):
        """test before 1916 - Bulgaria adopted teh Gregorain calendar in 1917"""
        assert calculateEaster.calcEaster(1905) == datetime.date(1905, 4, 30)

    def test_easter_2157(self):
        """Test Easter for 2157"""
        assert calculateEaster.calcEaster(2157) == datetime.date(2157, 5, 1)

    #    def test_easter_2163(self):
    #        assert calculateEaster.calcEaster(2163),datetime.date(2163,4,24))

    #
    def test_easter_2168(self):
        """Test Easter for 2168"""
        assert calculateEaster.calcEaster(2168) == datetime.date(2168, 5, 1)

    # test sql injection - only needed if we run a db

    def test_easter_not_integer_value_error(self):
        """test calculateEaster with a non-int input"""
        with pytest.raises(
            ValueError,
            match="The argument should be a valid year for which to calculate Easter Sunday",
        ):
            calculateEaster.calcEaster("tuesday")
