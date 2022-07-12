import unittest, pytest
import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src
import bgchofSettings
from src import generateCalendar
from src import fastingIO

# from src import bgchof
# from src import generateCalendar


class generateCalendarUnittest(unittest.TestCase):

    # check the length of the list for a Leap year
    def testGenerateListLeap(self):
        self.assertEqual(len(generateCalendar.generateList(2020)), 366)

    # check the length of the list for a non-Leap year
    def testGenerateListLeap(self):
        self.assertEqual(len(generateCalendar.generateList(2021)), 365)

    # check return type for an int (yearnumber)
    def testGenerateListReturnsListForIntYear(self):
        self.assertIsInstance(generateCalendar.generateList(2021), list)

    def testGenerateListIfAllElementsAre6(self):
        myTestList = generateCalendar.generateList(2020)
        for i in myTestList:
            self.assertEqual(myTestList[i], 6)

    def testGenerateList_NonInt_ValueError(self):
        with pytest.raises(
            ValueError, match="Please supply an int argument representing an year."
        ):
            generateCalendar.generateList("someSting")


if __name__ == "__main__":
    unittest.main()
