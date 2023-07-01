# **Metonic Cycle Calculator**

## Introduction
The metonic cycle, the enneadecaeteris, or the lunisolar cycle are all names for a natural cycle between the Earth and its moon that repeats every 19 years. This synchronization cycle and variations of it can predict the Moon's phase far in the future, and many ancient astronomers and mathematicians throughout history have spent much effort deriving them. The most famous use case for the metonic cycle is for the Computus--the algorithm that calculates future Easter dates(as the holiday must occur after a full moon phase). 

This calculator extends these metonic cycle calculations to most moons and their respective planets within the solar system. Given a synchronization error in days, the program will attempt a decimal expansion to calculate a ratio of planetary years to synodic moon periods with a smaller error. With this newfound metonic cycle, dates where  the sun, moon, and planet share the same relative configuration within the solar system can be calculated.

## Installation instructions:
>git clone https://github.com/arctangent4/metonic.git

>cd metonic

>pip install -r requirements.txt


Astroquery, requests, and numpy are the 3 external packages needed for the program. I do apologize for the large number of dependencies that astroquery requires.

## Running the program
You can run the program with just
>python input.py

and the program will guide you through providing inputs.
You can also run the program straight from the command line with the following syntax:
>python input.py [-h] [-n MOON_NAME] [-d DATE] [-e ERROR] [-nd NUM_DATES] [-s SKIP]

Details for these arguments are as follows:

**Required Arguments**:

  -n MOON_NAME, --moon_name ~
                        Name of the moon whose metonic cycle you want to investigate. Use its most commonly referred name e.g. Ganymede and not J3 or Jupiter III. Full list of supported moons can be found in satellites.json. Use 'Moon' for Earth's moon.
                        
**Optional Arguments**(defaults will be substituted):

  -h, --help     ~       show this help message and exit
  
  -d DATE, --date ~ target date from which similar metonic dates will be calculated.
  
  -e ERROR, --error  ~
                         a decimal margin of error(in Earth days) for the ratio between planet years and moon periods. This affects the type of cycle generated and its accuracy. For example, the Earth-Moon system has many possible cycles: the 8 year metonic cyle called the octaeteris, the more accurate and well known 19 year enneadecaeteris, and the even more accurate 76 year Callipic cycle. 
                        
  -nd NUM_DATES, --num_dates ~
                        Inputted as [x,y] list. Give the x number of prior metonic dates and the y number of future metonic dates you need(program will return the x previous metonic dates and y next metonic dates relative to the target date).
                        
 -s SKIP, --skip  ~ skips printed text and inputs

 ## Technical Details
The program uses NASA's JPL Horizons API for ephemeris data for objects in the solar system.
It grabs the period of the target moon and carries out a decimal expansion to approximate the ratio between the moon and the planet's periods.
Once an acceptable fraction approximation within error bounds is found, the program is able to construct a metonic cycle for the moon and planet.

Then, the program grabs data for a "S-T-O" parameter that is roughly similar to a phase angle that the sun, planet, and moon make with each other.
The program then selects data near the peak of the phase curve(near 180 degrees) and performs a scipy interpolation to determine the "new moon time" of the moon.
On tests with the Earth's Moon, the program can determine the new moon time to within 7 minutes of accuracy.
In this way, the current moon phase on the target date and its repetitions in a metonic cycle can be determined.

Lastly, the program calculates preceding and subsequent "metonic" dates using the metonic cycle.
These are essentially dates where the Sun, Planet, and Moon positions within the Solar System will roughly repeat.

Program Structure:

Run input.py

input.py -> grab_data.py (Make API Call, determine planet, determine moon period)

input.py -> metonic.py (Calculate Metonic Cycle)

input.py -> phase_calcs.py (Determine new moon time and phase at target date)

input.py does final calculations and returns results.
