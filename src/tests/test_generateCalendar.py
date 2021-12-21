from .context import bgchof
from .context import generateCalendar
import unittest

class generateCalendarUnittest(unittest.TestCase):

    # check the length of the list for a Leap year
    def testGenerateListLeap(self):
        self.assertEqual(len(generateCalendar.generateList(2020)),366)
    # check the length of the list for a non-Leap year
    def testGenerateListLeap(self):
        self.assertEqual(len(generateCalendar.generateList(2021)),365)
    #check return type for an int (yearnumber)
    def testGenerateListReturnsListForIntYear(self):
        self.assertIsInstance(generateCalendar.generateList(2021),list)
    #check return type for a non-int
    def testGenerateListReturnsNonetForNonInt(self):
        self.assertIsNone(generateCalendar.generateList('someString'))
    def testGenerateListIfAllElementsAre6(self):
        myTestList = generateCalendar.generateList(2020)
        for i in myTestList:
            self.assertEqual(myTestList[i],6)

if __name__ == '__main__':
    unittest.main()
