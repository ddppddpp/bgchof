from types import MemberDescriptorType
from typing import Match
import unittest
import datetime
import sys, os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import bgchofSettings
from src import calculateEasterSunday as calculateEaster


class easterUnittest(unittest.TestCase):
    def testEaster1983(self):
        # 20th century example from the Tipikon
        self.assertEqual(calculateEaster.calcEaster(1983), datetime.date(1983, 5, 8))

    def testEaster1995(self):
        # 20th century example two from the Tipikon
        self.assertEqual(calculateEaster.calcEaster(1995), datetime.date(1995, 4, 23))

    def testEaster2021(self):
        # 21th century example two
        self.assertEqual(calculateEaster.calcEaster(2021), datetime.date(2021, 5, 2))

    # test for leap year - known leap - i.e. 2012, 2020, also edge cases - 100s(non leap) and 400s(leap)
    # important tests for leap years are 1600, 2000 (leap) and 1700, 1800, 1900, 2100
    # edge cases - Apr24 - 30, May 1-7 - those dates are on the border b/w Apr and May in the Tipikon LuTs,
    # any errors in the calculations should fall there
    def testEaster1600(self):
        # Leap year 1600 (divisible by 100 but also divisible by 400)  Note - no Revised Julian for this date
        self.assertEqual(calculateEaster.calcEaster(1600), datetime.date(1600, 4, 2))

    def testEaster1700(self):
        # Non-leap year 1700 (divisible by 100)  Note - no Revised Julian for this date
        self.assertEqual(calculateEaster.calcEaster(1700), datetime.date(1700, 4, 11))

    def testEaster1800(self):
        # Non-leap year 1700 (divisible by 100)  Note - no Revised Julian for this date
        self.assertEqual(calculateEaster.calcEaster(1800), datetime.date(1800, 4, 20))

    def testEaster1900(self):
        # Non-leap year 1900 (divisible by 100)  Note - no Revised Julian for this date
        self.assertEqual(calculateEaster.calcEaster(1900), datetime.date(1900, 4, 22))

    def testEaster2000(self):
        # Leap year 2000 (divisible by 100 but also divisible by 400)
        self.assertEqual(calculateEaster.calcEaster(2000), datetime.date(2000, 4, 30))

    def testEaster2100(self):
        # 22th century example
        self.assertEqual(calculateEaster.calcEaster(2100), datetime.date(2100, 5, 2))

    def testEasterEmptyString(self):
        # test for empty string
        with pytest.raises(
            ValueError,
            match="The argument should be a valid year for which to calculate Easter Sunday",
        ):
            calculateEaster.calcEaster("")

    # important tests for leap years are 1600, 2000 (leap) and 1700, 1800, 1900, 2100
    # edge cases - Apr24 - 30, May 1-7 - those dates are on the border b/w Apr and May in the Tipikon LuTs,
    # 2016 - 01.05
    def testEaster2016(self):
        self.assertEqual(calculateEaster.calcEaster(2016), datetime.date(2016, 5, 1))

    # 2027 - 02.05
    def testEaster2027(self):
        self.assertEqual(calculateEaster.calcEaster(2027), datetime.date(2027, 5, 2))

    # 2054 - 03.05
    def testEaster2054(self):
        self.assertEqual(calculateEaster.calcEaster(2054), datetime.date(2054, 5, 3))

    # 2059 - 04.05
    def testEaster2059(self):
        self.assertEqual(calculateEaster.calcEaster(2059), datetime.date(2059, 5, 4))

    # 2013 - 05.05
    def testEaster2013(self):
        self.assertEqual(calculateEaster.calcEaster(2013), datetime.date(2013, 5, 5))

    # 2040 - 06.05
    def testEaster2040(self):
        self.assertEqual(calculateEaster.calcEaster(2040), datetime.date(2040, 5, 6))

    # 2051 - 07.05
    def testEaster2051(self):
        self.assertEqual(calculateEaster.calcEaster(2051), datetime.date(2051, 5, 7))

    # 2062 - 30.04
    def testEaster2062(self):
        self.assertEqual(calculateEaster.calcEaster(2062), datetime.date(2062, 4, 30))

    # 2057 - 29.04
    def testEaster2057(self):
        self.assertEqual(calculateEaster.calcEaster(2057), datetime.date(2057, 4, 29))

    # 2019 - 28.04
    def testEaster2019(self):
        self.assertEqual(calculateEaster.calcEaster(2019), datetime.date(2019, 4, 28))

    # 2087 - 27.04
    def testEaster2087(self):
        self.assertEqual(calculateEaster.calcEaster(2087), datetime.date(2087, 4, 27))

    # 2065 - 26.04
    def testEaster2065(self):
        self.assertEqual(calculateEaster.calcEaster(2065), datetime.date(2065, 4, 26))

    # 2060 - 25.04
    def testEaster2060(self):
        self.assertEqual(calculateEaster.calcEaster(2060), datetime.date(2060, 4, 25))

    # 2022 - 24.04
    def testEaster2022(self):
        self.assertEqual(calculateEaster.calcEaster(2022), datetime.date(2022, 4, 24))

    # test before 1916 - Bulgaria adopted teh Gregorain calendar in 1917
    def testEaster1905(self):
        self.assertEqual(calculateEaster.calcEaster(1905), datetime.date(1905, 4, 30))

    # 2157
    def testEaster2157(self):
        self.assertEqual(calculateEaster.calcEaster(2157),datetime.date(2157,5,1))
    
#    def testEaster2163(self):
#        self.assertEqual(calculateEaster.calcEaster(2163),datetime.date(2163,4,24))

    # 2168
    def testEaster2168(self):
        self.assertEqual(calculateEaster.calcEaster(2168),datetime.date(2168,5,1))

    # test sql injection - only needed if we run a db

    # test non-int
    def testEaster_NotInteger_ValueError(self):
        with pytest.raises(
            ValueError,
            match="The argument should be a valid year for which to calculate Easter Sunday",
        ):
            calculateEaster.calcEaster("tuesday")


if __name__ == "__main__":
    unittest.main()
