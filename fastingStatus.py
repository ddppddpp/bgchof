'''
each day of the year can be represented by an integer 0-6 with the following meaning

0 - no food allowed
1 - cold plant based food
2 - cooked plant based food
3 - oil/wine
4 - fish
5 - dairy, eggs
6 - meat


besides integer values I need a way to store text description in multiple languages

'''

def _(message):
    #once localization kicks in this function needs to be modified
    return str(message)
    
fastingStatusMessage = [_('No food allowed for this date!'),
                    _('raw plant based food'),
                    _('cooked plant based food'),
                    _('oil and wine'),
                    _('fish'),
                    _('milk/dairy, eggs'),
                    _('meat')
]

bodyDayMessage = _('According to the Bulgarian Christian Orthodox norms, on this day you can consume ')
andMessage = _(' and ')

def fastingValue2Msg(inputValue):
    returnMessage = ''
    n = 1
    if inputValue == 0:
        returnMessage = fastingStatusMessage[0]
    #try len(fastingStatusMessage)
    elif inputValue < 7:
        returnMessage = bodyDayMessage
        while n in range(1,inputValue):
            returnMessage = returnMessage + fastingStatusMessage[n] + ', '
            n+=1
        #strip 2 chars - the last comma and space
        returnMessage = returnMessage[:-2] + andMessage + fastingStatusMessage[inputValue] + '.'
    return returnMessage



#del _
#once localization kicks in this needs to be uncommented or the definitionof _() above modified

#debug
