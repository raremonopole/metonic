# **Metonic Cycle Calculator**

## Introduction
The metonic cycle, the enneadecaeteris, or the lunisolar cycle are all names for a natural cycle between the Earth and its moon that repeats every 19 years. This synchronization cycle and variations of it can predict the Moon's phase far in the future, and many ancient astronomers and mathematicians throughout history have spent much effort deriving them. The most famous use case for the metonic cycle is for the Computus--the algorithm that calculates future Easter dates. 

This calculator extends these metonic cycle calculations to most moons and their respective planets within the solar system. Given a synchronization error in days, the program will attempt a decimal expansion to calculate a ratio of planetary years to synodic moon periods with a smaller error. With this newfound metonic cycle, dates where  the sun, moon, and planet share the same relative configuration within the solar system can be calculated.

## Installation instructions:
>git clone https://github.com/arctangent4/metonic.git

>cd metonic

>pip install -r requirements.txt


Astroquery, requests, and numpy are the 3 external packages needed for the program.

## Running the program
You can run the program with just
>python input.py

and the program will guide you through providing inputs.
You can also run the program straight from the command line with the following syntax:
>python input.py [-h] [-n MOON_NAME] [-d DATE] [-e ERROR] [-nd NUM_DATES] [-s SKIP]

Details for these arguments are as follows:

**Required Arguments**:

  -n MOON_NAME, --moon_name MOON_NAME
                        Name of the moon whose metonic cycle you want to investigate. Use its most commonly referred name e.g Ganymede and not J3 or Jupiter III. Full list of supported moons can be found in satellites.json. Use 'Moon' for Earth's moon.
                        
**Optional Arguments**(defaults will be substituted):

  -h, --help            show this help message and exit
  
  -d DATE, --date DATE  target date from which similar metonic dates will be calculated.
  
  -e ERROR, --error ERROR
                         a decimal margin of error(in earth days) for the ratio between planet years and moon periods. This affects the type of cycle generated and its accuracy. For example, the Earth-Moon system has a 8 moon metonic cyle called Octaeteris, the more accurate and well known 19 year enneadecaeteris, and the even more accurate 76 year Callipic cycle. 
                        
  -nd NUM_DATES, --num_dates NUM_DATES
                        Inputted as [x,y] list. Give the x number of prior metonic dates and the y number of future metonic dates you need(program will return the x previous metonic dates and y next metonic dates relative to the target date).
                        
 -s SKIP, --skip SKIP  skips printed text and inputs
