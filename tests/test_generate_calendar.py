''' Tests for the the generateCalendar Module '''
import sys
from pathlib import Path

import pytest
from src import generateCalendar

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))




class TestCalendar:
    ''' A class of test functions. '''

    def test_generate_list_leap(self):
        '''check that the length of the list for a Leap year is 366 days'''
        assert len(generateCalendar.generate_list(2020)) == 366


    def test_generate_list(self):
        '''check the length of the list for a non-Leap year'''
        assert len(generateCalendar.generate_list(2021)) == 365


    def test_generate_list_returns_list_for_int_year(self):
        '''check return type for an list of ints (yearnumber)'''
        assert isinstance(generateCalendar.generate_list(2021), list)

    def test_generate_list_if_all_elements_are_sixes(self):
        '''Test if generate_list returns a list of statuses of six'''
        my_test_list = generateCalendar.generate_list(2020)
        for i in my_test_list:
            assert my_test_list[i] == 6

    def test_generate_list_non_int_value_error(self):
        ''' Test if a ValueError is raised when trying to call
            generate_list with an non-int argument.
        '''
        with pytest.raises(
            ValueError, match=r"Please supply an int argument representing an year\."
        ):
            generateCalendar.generate_list("someString")
