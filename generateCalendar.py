from datetime import date, timedelta
import calculateEaster
import sys

def generateList(inputYear):
    fastingList = []
    if type(inputYear)is int:
        firstDay = date(inputYear,1,1)
        lastDay = date(inputYear,12,31)
        for n in range(int ((lastDay - firstDay).days)+1):
            fastingList.append(6)
        return fastingList
    else:
        return None

def generateBaseFasting(inputYear, inputList):
    #starting Jan 1st set the statuses for the base, 1-day fasting rules:
    firstDay = date(inputYear,1,1)
    lastDay = date(inputYear,12,31)
    #single day fasting

    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        #each wed, fri -  4 (fish)
        if ((day.weekday()== 2) or (day.weekday() == 4)):
            inputList[n] = 4
    #Jan 5 is the day before Holy Epiphany - 2 (no oil); if  on Sat or Sun -> 3 (plus oil)
    janFive = date(inputYear,1,5)
    if (janFive.weekday() > 4):
        inputList[4] = 3
    else:
        inputList[4] = 2
    #Aug 29 - 2 (no oil) ; if  on Sat or Sun -> 3 (plus oil)
    augTwentyNine = date(inputYear,8,29)
    augTwentyNineYearDay = yearDayCurrYear(augTwentyNine)
    if (augTwentyNine.weekday() > 4):
        inputList[augTwentyNineYearDay-1] = 3
    else:
        inputList[augTwentyNineYearDay-1] = 2
    #Sept 14 - 3 (hot food, cold food, plant based oil)
    septFourteen = date(inputYear,9,14)
    septFourteenYearDay = yearDayCurrYear(septFourteen)
    inputList[septFourteenYearDay-1] = 3
    #<goodFri> - 0 - no food, no water
    #Easter Sunday calculation is expensive, try to do it once per calendar generation and then send it all procedures

    #return just the list as the calndar is global, is that ok?
    return inputList

def resurrectionFast(inputDate, inputList):
    #the resurreciton starts 7 weeks before Easter Sunday
    #one week before that there's a fast-free (6) week of preparation (1st 7 days)
    #0th week of the fast - all days - dairy/eggs (5)
    #1st week - mon - sat 2, sun 3
    #2nd week - check for Annunciation - March 25
    #3nd through 5th week - mon-fri 2, sat-sun 3
    #week 6 - mon-fri 2, sat - 3, sun 4 - Palm Sunday
    #week 7 - mon-thu 2, fri - 6, sat 3, sun - Easter Sunday
    #The week from Easter Sunday through Thomas Sunday is fast-free (6)
    firstDay = inputDate
    #print(firstDay.strftime('%d-%m-%Y'))
    for n in range(1,8): #next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day)-1] = 6
    firstDay = day
    #print(firstDay.strftime('%d-%m-%Y'))
    for n in range(1,8): #next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day)-1] = 5
    firstDay = day
    #print(firstDay.strftime('%d-%m-%Y'))
    for n in range(1,8): #next 7 days
        day = firstDay + timedelta(days=n)
        if (day.weekday() <6):
            inputList[yearDayCurrYear(day)-1] = 2
        else:
            inputList[yearDayCurrYear(day)-1] = 3
    firstDay = day
    for n in range(1,29): #next 28 days
        day = firstDay + timedelta(days=n)
        if (day.weekday() <5):
            inputList[yearDayCurrYear(day)-1] = 2
        else:
            inputList[yearDayCurrYear(day)-1] = 3
    firstDay = day
    for n in range(1,8): #next seven days
        day = firstDay + timedelta(days=n)
        if (day.weekday() <5):
            inputList[yearDayCurrYear(day)-1] = 2
        elif (day.weekday() == 5):
            inputList[yearDayCurrYear(day)-1] = 3
            #print('Palm Sunday ',day.strftime('%d-%m-%Y'))
        else:
            inputList[yearDayCurrYear(day)-1] = 4
    firstDay = day
    for n in range(1,8): #next seven days
        day = firstDay + timedelta(days=n)
        if (day.weekday() <4):
            inputList[yearDayCurrYear(day)-1] = 2
        elif (day.weekday() == 4):
            inputList[yearDayCurrYear(day)-1] = 0
        elif (day.weekday() == 5):
            inputList[yearDayCurrYear(day)-1] = 3
        else:
            inputList[yearDayCurrYear(day)-1] = 6
    firstDay = day
    for n in range(1,8): #next seven days
        day = firstDay + timedelta(days=n)
        inputList[yearDayCurrYear(day)-1] = 6

    #the Annunciation if celebrated on March 25 (fixed)
    #if this is not in the Holy Week, fish is allowed
    #check for Holy Week
    inputList[yearDayCurrYear(date(inputDate.year,3,25))-1] = 4

    return inputList

def stPeterAndPaulFast(pentecostDate, inputList):
    #St Peter's Fasts start on the Monday after the 1st Sunday after Pentecost
    #it ends on June 29th (fixed) - st Peter & Paul
    #find the 1st sunday after pentecostDate

    #TODO - check if there are 14 days b/w start and 29th.
    # if yes - we need one 'fast free' week (status 6) before the fast starts
    if pentecostDate.weekday() == 6:
        firstDay = pentecostDate
    else:
        firstDay = pentecostDate
        while firstDay.weekday() < 7:
            firstDay += timedelta(days=1)
    #print('first sunday after penetecost',firstDay.strftime('%d-%m-%Y'))
    firstDay += timedelta(days=1) #we actually start *after* the 1st sunday
    lastDay = date(pentecostDate.year,6,28) #lastDay is June 28 - the day before St. Peter and Paul's feast - fixed
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        if (day.weekday() == 2) or (day.weekday() == 4):
            inputList[yearDayCurrYear(day)-1] = 3
        else:
            inputList[yearDayCurrYear(day)-1] = 4



    return inputList

def dormitionFast(inputYear, inputList):
    # The Dormition of the Mother of God is celebrated on Aug 15 as a fixed day
    # The fasting starts on Aug 1 and ends on Aug 15. It is the 2nd most strict fast during the year
    # Only cold food (1) is allowed on Mon, Wd, Fri
    # On Tue, Thu - cooked food (2)
    # Sat, Sun - oil and wine (3)
    # The Transfiguration of Our Lord is celebrated on Aug 6, so fish is allowed on this day (4)
    # If Aug 15 is on a Wed/Fri fish is allowed (4) <--- need to verify what to do on Sat/Sun Aug 15
    firstDay = date(inputYear,8,1)
    lastDay = date(inputYear,8,15)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        if (day.weekday()==0) or (day.weekday()==2) or (day.weekday()==4):
            inputList[dayNumber-1] = 1
        elif (day.weekday()==1) or (day.weekday()==3):
            inputList[dayNumber-1] = 2
        elif (day.weekday()>4):
            inputList[dayNumber-1] = 3
    #Aug 6
    inputList[yearDayCurrYear(date(inputYear,8,6))-1] = 4
    #Aug 15
    if(date(inputYear,8,15).weekday()==2 or date(inputYear,8,15).weekday()==4):
        inputList[yearDayCurrYear(date(inputYear,8,15))-1] = 4
    #All done - return the list
    return inputList

def nativityFast(inputYear, inputList):
    #The Nativity Fast is on fixed dates each year
    #It starts on Nov15 (a day after St Philip)
    #Nov15 - Nov22 - Oil& Wine (3)
    #Nov23 - Dec19 - Fish (4) if not Wed or Fri
    #Dec20 - Dec24 - Oil & Wine (3)
    #Dec25 - Jan4 - No fasting (meat - 6)
    firstDay = date(inputYear, 11,15)
    lastDay = date(inputYear,11,22)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber-1] = 3
    firstDay = date(inputYear, 11,23)
    lastDay = date(inputYear,12,19)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        if ((day.weekday()!= 2) and (day.weekday() != 4)):
            inputList[dayNumber-1] = 4
        else:
            inputList[dayNumber-1] = 3
    firstDay = date(inputYear, 12,20)
    lastDay = date(inputYear,12,24)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber-1] = 3
    firstDay = date(inputYear, 12,25)
    lastDay = date(inputYear,12,31)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber-1] = 6
    firstDay = date(inputYear, 1,1)
    lastDay = date(inputYear,1,4)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        dayNumber = yearDayCurrYear(day)
        inputList[dayNumber-1] = 6
    return inputList

def yearDayCurrYear(inputDate):
    #for a given date calculate the day number within the year
    return (inputDate.toordinal() - date(inputDate.year,1,1).toordinal() + 1)

def printCalendar(inputYear, inputList):
    #debugging purposes - print a list of dates and fasting status
    # example with similar iteration https://blog.finxter.com/iterating-through-a-range-of-dates-using-python-with-datetime/

    firstDay = date(inputYear,1,1)
    lastDay = date(inputYear,12,31)
    for n in range(int ((lastDay - firstDay).days)+1):
        day = firstDay + timedelta(days=n)
        #print(day.strftime('%d-%m-%Y'),',',day.weekday(),inputList[n])
        print(day.strftime('%d-%m-%Y'),',',day.strftime("%a"),inputList[n])

def fastingYearList(inputYear):
    fastingList = generateList(inputYear)
    generateBaseFasting(inputYear,fastingList)
    easterDate = calculateEaster.calcEaster(inputYear)
    easterFastStartDate = easterDate - timedelta(days=63)
    resurrectionFast(easterFastStartDate, fastingList)
    pentecostDate = easterDate + timedelta(days=49) #the 50th date after Easter Sunday
    stPeterAndPaulFast(pentecostDate, fastingList)
    dormitionFast(inputYear,fastingList)
    nativityFast(inputYear,fastingList)

    return fastingList

def getVeganDays(inputList):

    veganDays = 0
    for n in range(len(inputList)):
        if int(inputList[n])<4:
            veganDays+=1
    return veganDays

def getVegetarianDays(inputList):
    vegetarianDays = 0
    for n in range(len(inputList)):
        if int(inputList[n])>3 and int(inputList[n])<6:
            vegetarianDays+=1
    return vegetarianDays
'''
#debug
myTestYear = 2021
easterDate = calculateEaster.calcEaster(myTestYear)

#it is import to call the procedures in turn so they initialize the dates in the right way
myList = generateList(myTestYear)
generateBaseFasting(myTestYear,myList)
easterDate = calculateEaster.calcEaster(myTestYear)
#fasting starts 7 weeks before Easter Sunday, preceeded by a fast-free weeks and a dairy/eggs week
easterFastStartDate = easterDate - timedelta(days=63)
resurrectionFast(easterFastStartDate, myList)
pentecostDate = easterDate + timedelta(days=49) #the 50th date after Easter Sunday
print('Pentecost', pentecostDate.strftime('%d-%m-%Y'))
stPeterAndPaulFast(pentecostDate, myList)
dormitionFast(myTestYear,myList)
nativityFast(myTestYear,myList)
printCalendar(myTestYear, myList)
print(easterFastStartDate.strftime('%d-%m-%Y'))
print(easterDate.strftime('%d-%m-%Y'))

'''

def main(argv):
    #check for number of arguments - should be one (year) plus one (name of program itself)
    if (len(argv) > 2) or (len(argv) < 2):
        sys.stderr.write("USAGE: %s <year for which to generate a fasting caledndar in format YYYY> \n" % (argv[0])) 
        return None
    else:
        sInputYear = argv[1]
    #check for valid type
    try:
        iInputYear = int(sInputYear)
    except ValueError:
        sys.stderr.write("The argument should be an year for which to generate a fasting calendar\n")
    # do some validation if needed
    #generate the lsit
    #it is import to call the procedures in turn so they initialize the dates in the right way
    myList = fastingYearList(iInputYear)
    return myList

if __name__ == "__main__":
    sys.exit(main(sys.argv)) 
