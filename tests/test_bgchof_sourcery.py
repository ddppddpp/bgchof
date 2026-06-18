import sys
from datetime import date

import pytest

from bgchof import (
    get_fasting_message_for_date,
    get_status_for_date,
    getFastingMessageForDate,
    getStatusForDate,
    main,
)


# Parametrized test for get_fasting_message_for_date with various realistic test values
@pytest.mark.parametrize("input_date, expected_output, test_id", [
    (date(2023, 1, 1), "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "happy_path_2023_01_01"),
    (date(2023, 4, 16), "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "happy_path_2023_04_16"),
    (date(2023, 12, 31), "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "happy_path_2023_12_31"),
])
def test_get_fasting_message_for_date(input_date, expected_output, test_id):
    # Act
    result = get_fasting_message_for_date(input_date)

    # Assert
    assert result == expected_output, f"Test failed for {test_id}"

# Parametrized test for get_status_for_date with various realistic test values
@pytest.mark.parametrize("input_date, expected_status, test_id", [
    (date(2023, 1, 1), 6, "happy_path_2023_01_01"),
    (date(2023, 4, 16), 6, "happy_path_2023_04_16"),
    (date(2023, 12, 31), 6, "happy_path_2023_12_31"),
])
def test_get_status_for_date(input_date, expected_status, test_id):
    # Act
    status = get_status_for_date(input_date)

    # Assert
    assert status == expected_status, f"Test failed for {test_id}"

# Parametrized test for deprecated functions with various realistic test values
@pytest.mark.parametrize("input_date, expected_status, expected_message, test_id", [
    (date(2023, 1, 1), 6, "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "deprecated_2023_01_01"),
    (date(2023, 4, 16), 6, "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "deprecated_2023_04_16"),
])
def test_deprecated_functions(input_date, expected_status, expected_message, test_id):
    # Act
    status = getStatusForDate(input_date)
    message = getFastingMessageForDate(input_date)

    # Assert
    assert status == expected_status, f"Status test failed for {test_id}"
    assert message == expected_message, f"Message test failed for {test_id}"

# Parametrized test for main function with various edge cases and error cases
@pytest.mark.parametrize("argv, expected_output, test_id", [
    ([], None, "error_no_args"),
   # (["bgchof.py"], get_fasting_message_for_date(date.today()), "happy_path_today"),
    (["bgchof.py", "2023-01-01"], "According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.", "happy_path_specific_date"),
    (["bgchof.py", "2023-01-01", "extra_arg"], None, "error_extra_arg"),
    (["bgchof.py", "invalid-date"], None , "error_invalid_date"),
])
def test_main(argv, expected_output, test_id, monkeypatch, capsys):
    """Test the main function with various command-line arguments.

    Tests both successful execution with valid dates and error handling
    for invalid inputs like missing arguments, extra arguments, and
    malformed date strings.
    """
    # Arrange
    def mock_exit(code):
        return code
    monkeypatch.setattr(sys, 'exit', mock_exit)

    # Act
    result = main(argv)

    # Assert
    if expected_output is None:
        captured = capsys.readouterr()
        assert captured.err, f"Test failed for {test_id}"
    else:
        assert result == expected_output, f"Test failed for {test_id}"
