"""A module that transforms fasting status values into messages.

Each day of the year can be represented by an integer 0-6 with the following meaning

0 - no food allowed
1 - cold plant based food
2 - cooked plant based food
3 - oil/wine
4 - fish
5 - dairy, eggs
6 - meat


besides integer values I need a way to store text description in multiple languages

"""


def _(message):
    # once localization kicks in this function needs to be modified
    return str(message)


fastingStatusMessage = [
    _("No food allowed for this date!"),
    _("raw plant based food"),
    _("cooked plant based food"),
    _("oil and wine"),
    _("fish"),
    _("milk/dairy, eggs"),
    _("meat"),
]

BODY_DAY_MESSAGE = _(
    "According to the Bulgarian Christian Orthodox norms, on this day you can consume "
)
AND_MESSAGE = _(" and ")


def fasting_value_to_message(input_value):
    """Form the user-friendly message with allowed food.

    Args:
        input_value: int(0..6) - the fasting status value for a date.
    Returns:
        return_message: String with a comma-separated food options allowed for that date.

    """
    return_message = ""
    n = 1
    if input_value == 0:
        return_message = fastingStatusMessage[0]
    # try len(fastingStatusMessage)
    elif input_value < 7:
        return_message = BODY_DAY_MESSAGE
        while n in range(1, input_value):
            return_message = return_message + fastingStatusMessage[n] + ", "
            n += 1
        # strip 2 chars - the last comma and space
        return_message = (
            return_message[:-2] + AND_MESSAGE + fastingStatusMessage[input_value] + "."
        )
    return return_message


# del _
# once localization kicks in this needs to be uncommented or the definitionof _() above modified
