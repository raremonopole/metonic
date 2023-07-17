#External Imports
import sys
import math
from fractions import Fraction
import datetime 
import argparse
# from collections import OrderedDict
import ast

#Project Imports
from metonic import metonic_cycle_calc 
from phase_calcs import calculate_moon_phase, calc_phase_zero_point
from grab_data import grab_moon_info, make_horizons_call 



#PARSE ARGUMENTS
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--moon_name", help="Name of the moon whose metonic cycle you want to investigate. Use its most common \
                    ly referred name e.g Ganymede and not J3 or Jupiter III. Full list of supported moons can be found in satellites.json. Use 'Moon' for Earth's moon.")

parser.add_argument("-d", "--date", default=datetime.datetime.now(), help="target date from which similar metonic dates will be calculated.")
parser.add_argument("-e", "--error",type=float, default=.5, help="        a decimal margin of error(in earth days) for the ratio between planet years and moon periods. This affects the type of cycle generated and its accuracy. For example, the Earth-Moon system has a 8 moon metonic cyle called Octaeteris, the more accurate and well known 19 year enneadecaeteris, and the even more accurate 76 year Callipic cycle. ")
parser.add_argument("-nd", "--num_dates", default=[3,3], help="Inputted as [x,y] list. Give the x number of prior metonic dates and \
                    the y number of future metonic dates you need(program will return the x previous metonic dates and y next metonic dates relative to the target date).")


parser.add_argument("-s", "--skip",default=False, help="An optional flag to skip printed text and inputs")


#Alternative to required=True, allows user to provide moon name without having to rerun the program.
args = parser.parse_args()
if not args.moon_name:
    cont_flag = input("\nError: no moon name provided, and it is required. You can press i to input it now, or exit with any other key. Run python input.py --help for further details.  \n")
    if cont_flag.lower()=="i":
        args.moon_name = input("\nInput the moon name: ")

    else:
        print("Exiting... \n")
        exit()

#EDIT ARGUMENTS
if args.skip==False:
    #If skip isn't used, we don't it to be enumerated in the list of arguments later on.
    delattr(args,"skip")
    print("""\nWelcome to the metonic cycle calculator. This will calculate the length of an approximate metonic cycle for any planet and respective moon. 
Then, you can ask find all dates where the sun, the planet, and its moon are in the same configuration relative to each other. But keep in mind that shifts in planetary
orbits and calculation error make our approximation rough. The most famous use of a metonic cycle calculation is to find
future dates of Easter--as the holiday has to occur on the Sunday that follows the first full full moon after March 21st(the spring equinox). \n """)

    #Set up this way to make creating arg_zip easier
    iter_args = vars(args)
    arg_values = [getattr(args,arg) for arg in iter_args]

    #Printing inputted Arguments
    print(f"Here are the argument inputs(defaults substituted in):")
    for idx, arg in enumerate(iter_args):
        print(f"{arg}: {arg_values[idx]}")
    cont_flag = input("\nIf you would like to change any of the arguments, press i. Press x to exit. Otherwise, press any other key to commence the calculation.\n")

    #Zip arg keys and arg values to iterate over in the branching editing loop.
    #lower() just in case input is capitalized
    arg_zip = zip(iter_args.keys(), arg_values)
    if cont_flag.lower()=="i":

        for _,(arg, arg_val) in enumerate(arg_zip):

            print(f"\n{arg_val} is the value of the {arg} argument.")
            cont_flag = input(f"*If you would like to change this argument, press y. Otherwise, press any key to skip.\n")

            if cont_flag.lower()=="y" or cont_flag.lower()=="yes":
                new_val = input(f"Please input the value you want for the {arg} argument(press h for help, x to skip): ")

                if new_val.lower() == "h":

                    print(f"Here is help for the {arg} argument: \n")
                    print(parser.get_argument(f"{arg}").help)
                    new_val = input(f"Please input a value for the {arg} argument or press x to skip")

                if new_val.lower() != "x":
                    setattr(args,arg,new_val)
                    print(f"\nArgument {arg} successfully edited to equal {new_val}!\n")

    elif cont_flag.lower()=="x":
        exit()


    print("Commencing calculation. Please wait a few moments as the API call and calculation can take some time. \n")



moon_name = args.moon_name
input_date = args.date
synchronization_error = float(args.error)
num_dates = args.num_dates

#VALIDATE ARGUMENTS
moon_name.capitalize
if not isinstance(input_date, datetime.datetime):
    try:
        format_input_date = datetime.datetime.strptime(input_date, '%m-%d-%Y %H:%M:%S')
        
    #ValueError triggers if first pattern fails.
    except ValueError:
        try:
           format_input_date = datetime.datetime.strptime(input_date, '%m/%d/%Y %H:%M:%S')

        except ValueError:
            raise Exception(f"Error processing input_date. Make sure it is in m/d/y H:M:S or m-d-y H:M:S format.")
        
    input_date = format_input_date

elif not isinstance(num_dates, list):
    try:
        #Sometimes list input is not interpreted correctly. ast should turn the input into a list.
        num_dates = ast.literal_eval(num_dates)
        if len(num_dates) != 2:
            raise Exception(f"Error. num_dates must be a list with two elements, [x,y]. Use python input.py --help for more info. Make sure to include \
                the square brackets when inputting the list.")



    except Exception(f"Error. num_dates must be a list with two elements, [x,y]. Use python input.py --help for more info. Make sure to include \
                        the square brackets when inputting the list.")



#GRAB DATA AND CALCULATE BASIC PARAMETERS
(planet_name,planetary_year) = grab_moon_info(moon_name)
ephem_data, moon_period = make_horizons_call(moon_name, planet_name,planetary_year, input_date)


#Need to convert datatypes due to numpy intricacies.
time_data = ephem_data[0]
phase_angles = [float(i) for i in ephem_data[1]]


#Find nearest new_moon_time and find the moon phase of the selected date.
new_moon_time = calc_phase_zero_point(time_data, phase_angles)
print(f"\nThe nearest new moon date for{' the' if moon_name=='Moon' else ''} {moon_name} is {new_moon_time} UTC")

moon_phase = calculate_moon_phase(input_date, moon_period, new_moon_time)


#CALCULATE METONIC CYCLE AND FIND DATES
#Actually calculate the metonic cycle, and then use the cycle to find other dates where the Sun-Planet-Moon configuration roughly repeats.
(approx_planet_years, approx_moon_periods, error) = metonic_cycle_calc(synchronization_error, planetary_year, moon_period)

def find_metonic_dates(target_date, num_periods, period_length, num_dates):
    #convert cycle length to seconds. Remember moon period is in Earth days.
    cycle_length = num_periods*period_length*24*3600
    #cycle_indices creates a list of cycle multiples to add or subtract from the target date.
    cycle_indices = list(range(-num_dates[0], 0)) + list(range(1, num_dates[1] + 1))
    cycle_dates = [target_date+datetime.timedelta(seconds=(index*cycle_length)) for index in cycle_indices]
    
    return cycle_dates

metonic_dates = find_metonic_dates(input_date, approx_moon_periods, moon_period, num_dates)

#RETURN OUTPUT TO USER
#Note: This is the best place to pass values from this program to another program if wanted.

output_text = f"""
Calculation finished. At {input_date}, {'the ' if moon_name=="Moon" else ''}{moon_name} will be in a {moon_phase} phase. 
The metonic cycle is a ratio of {approx_planet_years} {planet_name} year(s) to {approx_moon_periods} {moon_name} synodic periods.

You requested {num_dates[0]} prior metonic dates and {num_dates[1]} future metonic dates. Here they are:
"""

print(output_text)

for date in metonic_dates:
    print(date," UTC")







        


    

