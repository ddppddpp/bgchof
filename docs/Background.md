### Background ###
The Christian Orthodox Fasting Code is a complex system of rules, ranging in extremes from no food or water allowed (on Good Firday) to no restrictions (i.e. weeks after long fasting periods).
The rules are a combination of some that are fixed (i.e. Dormition of Mary Mother of God is celebrated each year on Aug 15 fixed) and others that are changing based on Easter Sunday (i.e. the Easter Fast).
To make things even more complex the Bulgarian Christian Orthodox Church celebrates Easter Sunday according to the (Revised) Julian Calendar, but goes western-style for the Nativity Holiday (Dec 24) matching the Gregorian Calendar (Unlike other Orhtodox churhes such as the  Serbian, Macedonian, Russian, etc.).
Easter Sunday is between Apil 4th and May 11th for the 20th and 21st centuries (see Correction for Century).
For a description of the various fasting periods please see [FASTINGRULES](docs/FASTINGRULES.md)



Throughout this module the following coding is used to represent food value:

0. no food allowed
1. cold plant based food
2. cooked plant based food
3. oil/wine
4. fish
5. dairy, eggs
6. meat

Invertebrate based food i.e. seafood or snails is generally considered equal to plant based and allowed on most days.

Rules go in increasing manner with each value imposing less restrictions, meaning that on days with a code value of 0 no food is allowed, on days with a value of 3 cold plant based food, cooked plant based food, oil and wine are allowed, etc. and on days with a value of 6 there are no restrictions