# (B)ul(g)arian (Ch)ristian (O)rthodox (F)asting #

## A module for calculating the allowed food diet according to the fasting rules of the Bulgarian Christian Orthodox Church as published in the 1980 Tipikon ##

### Purpose ###
- Easy caluclation of the fasting diet for a particular date/week/month/period, i.e. 'What can I/can't I eat today'
- An excercise in Python
- This library is the backend for my project [nocmu.me](https://nocmu.me) - a React-based GUI hosted on [GitHub Pages](https://pages.github.com), talking to a [FastAPI](https://fastapi.tiangolo.com) - based backend that lives (and dies and lives again) as an [AWS Lambda](https://aws.amazon.com/lambda/).


Important [Disclaimer](docs/Disclaimer.md)


### Installation ###

Create a local directory and issue the following command to get an up-to-date copy of all files.

```
git clone https://github.com/ddppddpp/bgchof
```

### Usage ###

**CLI usage** is supported, by invoking the python file bgchof.py with either no arguments (default to current date) or specific date in yyyy-mm-dd format.

Example:
```
% python bgchof.py               
According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine and fish.
bgchof % python bgchof.py 1953-05-07
According to the Bulgarian Christian Orthodox norms, on this day you can consume raw plant based food, cooked plant based food, oil and wine, fish, milk/dairy, eggs and meat.

```
...or you can bring up a local [Flask based API](docs/Flask_API.md).

For more info on Fasting please see [Background](docs/Background.md) and [FASTINGRULES](docs/FASTINGRULES.md).

The code documentation is available in [Modules](docs/Modules.md).




## License ##
[License information](LICENSE)

## References ##

(ToDo)Typikon Link (still looking for a valid link)

A Python module for calculating the dates of Easter Sunday for the Julian, Revised Julian, and Gregorian Calendars by github user mattsmi https://github.com/mattsmi/EasterCalcsPython3

An article in Bulgarian describing in details the rules http://www.pravoslavieto.com/docs/post/postite_v_BPC.htm

A very well documented online calendar site in English, French and Bulgarian by Petko Yotov: http://5ko.free.fr/bg/year.php

An actively developed site in Bulgarian with PDFs of the [calendars](http://apostolite.com/category/постен-календар/).