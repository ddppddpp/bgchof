# (B)ul(g)arian (Ch)ristian (O)rthodox (F)asting #

## A module for calculating the allowed food diet according to the fasting rules ##
## of the Bulgarian Christian Orthodox Church ##
## as published in the 1980 Tipikon ##

### Purpose###
Easy caluclation of the allowed/forbidden food for a particular date/week/month/period


### Disclaimer ###
While Christian Orthodox fasting is a process of spiritual abstaining from sin rather than an ordeal for the phisical self, this module focuses only on its culinary side. The restrictions vary from trivial (i.e. red meat and poultry are not allowed, however fish can still be consumed) to very strict (i.e. no food or water on Good Friday) and could potentially be harmful for the body. By all means, if anybody considers fasting of any kind they shoud seek medical AND spiritual advice first.
Please treat this code as an excercise in programming, not as any kind of diet instructions.

### Usage ###
Currenly, only CLI usage is supported, by invoking the python file bgchof.py with either no arguments (default to current date) or specific date in yyyy-mm-dd format.

Example:
```
% python bgchof.py               
According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine and fish.
bgchof % python bgchof.py 1953-05-07
According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.

```


### Background###
The Christian Orthodox Fasting Code is a complex system of rules, ranging in extremes from no food or water allowed (on Good Firday) to no restrictions (i.e. weeks after long fasting periods).
The rules are a combination of some that are fixed (i.e. Dormition of Mary Mother of God is celebrated each year on Aug 15 fixed) and others that are changing based on Easter Sunday (i.e. the Easter Fast).
To make things even more complex the Bulgarian Christian Orthodox Church celebrates Easter Sunday according to the (Revised) Julian Calendar, but goes western-style for the Nativity Holiday (Dec 24) matching the Gregorian Calendar (Unlike other Orhtodox churhes such as the  Serbian, Macedonian, Russian, etc.).
Easter Sunday is between Apil 4th and May 11th for the 20th and 21st centuries (see Correction for Century).
For a description of the various fasting periods please see [FASTINGRULES](docs/FASTINGRULES.md)



Throughout this module the following coding is used to represent food value:

0 - no food allowed
1 - cold plant based food
2 - cooked plant based food
3 - oil/wine
4 - fish
5 - dairy, eggs
6 - meat

Invertebrate based food i.e. seafood or snails is generally considered equal to plant based and allowed on most days.

Rules go in increasing manner with each value imposing less restrictions, meaning that on days with a code value of 0 no food is allowed, on days with a value of 3 cold plant based food, cooked plant based food, oil and wine are allowed, etc. and on days with a value of 6 there are no restrictions

### Modules ###

#### bgchof.py ####

main moudle. Can be invoked from the CLI with a date and prints out a string, formatted with the types of food allowed for this given date

#### fastingIO.py ####

an i/o module with functions for reading from and writing to a .csv file in the format (int daynumber, int(0-6) status)

#### generateCalendar.py ####

#can be invoked from the CLI with one int argument (year) - does what???

a list of procedures that calculate the fasting status for each day in a list 
**(list) fastingYearlist(int year)** - returns a list in the format 'dayNumber', 'fastingStatus' where dayNumber is the number of the day in the calendar year (Jan 1st = 1, Dec 31st = 365/6) and fastingStatus is [0..6]

**generateList(inputYear)** - returns a list with a number of elements equal to the number of days in inputYear. Each element is assigned a value of '6' (everything allowed, nor restrictions)

**generateBaseFasting(inputYear, inputList)** - goes through inputList and applies the base fasting rules



**calculateEaster.py **

Calculate Easter according to the Bulgarian Christian Orthodox Church Typikon (1980 edition, p. 510-512)
for use in i.e. time shifting holidays and fasting

Easter Sunday should be the 1st Sunday after the first full moon after the Spring Equinox

According to Bulgarian Christian Orthodox Typikon,
the date of easter is found by dividing the year by 28 and by 19 and using lookup tables

the result should be b/w APR 4 and May 11

Correction for Century

The look-up-tables in the Tipikon themselves are only valid for years 1900-2099.
The correction factor for Gregorian vs Julian calendars should be applied as follows
5.10.1582 - 28.02.1700 - 10 days (-3 delta from the Tipikon)
29.02.1700 - 28.02.1800 - 11 days (-2 delta)
29.02.1800 - 28.02.1900 - 12 days (-1 delta)
2100 +   14 days (+1 delta)
more here http://5ko.free.fr/bg/jul.php



## References ##

Typikon Link

A Python module for calculating the dates of Easter Sunday for the Julian, Revised Julian, and Gregorian Calendars by github user mattsmi https://github.com/mattsmi/EasterCalcsPython3

An article in Bulgarian describing in details the rules http://www.pravoslavieto.com/docs/post/postite_v_BPC.htm

A very well documented online calendar site in English, French and Bulgarian by Petko Yotov: http://5ko.free.fr/bg/year.php
