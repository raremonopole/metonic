import datetime
import numpy as np
import math

#FIND MOON PHASE
def calculate_moon_phase(target_date, moon_period, new_moon_date):
    moon_phases = [
    "New Moon",
    "Waxing Crescent",
    "First Quarter",
    "Waxing Gibbous",
    "Full Moon",
    "Waning Gibbous",
    "Last Quarter",
    "Waning Crescent"
]
    #Must have moon_period in seconds for greatest accuracy
    moon_period = moon_period*24*3600
    moon_phase_length = moon_period/8
    elapsed_time = (target_date - new_moon_date).total_seconds()
    _,cycle_rem = divmod (elapsed_time, moon_period) 
    phase_index = math.floor((cycle_rem/moon_phase_length))
    phase_name = moon_phases[phase_index]

    return phase_name


#FIND NEW MOON TIME. WORK IN PROGRESS
def calc_phase_zero_point(times, angles):
    times = [datetime.datetime.strptime(time_str, '%Y-%b-%d %H:%M') for time_str in times]
    # angles = [float(angle) for angle in angles]
    #Explicitly defining lengths for faster execution later.
    times_length = len(times)
    angles_length = len(angles)
    if (times_length<5) or (times_length!=angles_length):
        print("Raise exception")

    #Iteration to generate a list of angle changes
    angle_changes = np.array([])
    for i in range(times_length-1):
        time_diff = times[i+1] - times[i]
        time_diff = time_diff.total_seconds()
        angle_diff = angles[i+1] - angles[i]
        angle_changes = np.append(angle_changes, angle_diff/time_diff)    


    #Need to keep angle changes to assert change direction, so we assign absolute value to new variable
    abs_changes = np.absolute(angle_changes)
    average_change = np.average(abs_changes)

     #We'll sample the third angle. This allows us to check the preceding and following angles for increasing/decreasing behavior.
    initial_angle = angles[2]
    change_direction = assert_phase_angle_change(angle_changes)

    if change_direction=="positive":
        seconds_from_new_moon = (180-initial_angle/average_change)

    elif change_direction=="negative":
        seconds_from_new_moon = -(initial_angle)/(average_change)
        
 

    new_moon_time = times[2]+datetime.timedelta(seconds=seconds_from_new_moon)
    return new_moon_time


#If the phase angle is increasing, the moon is moving towards a full moon phase. If it is decreasing, the moon is moving towards a new moon phase.
#This should work for both prograde and retrograde orbits. 
#Interpolation code will be added in the future to account for the case where the moon
#is near a new moon phase at the target_date; otherwise, the program may extrapolate in the wrong direction.
#As long as step_size is no larger than 3h, this should be enough to extrapolate Metis's new moon time.

#Taking products asserts signs of angle changes. Similar thing can be done with abs values e.g abs(a)+abs(b)==abs(a+b)
def assert_phase_angle_change(angle_changes):
    if (angle_changes[0] or angle_changes[1] or angle_changes[2])==0:
        print("Sorry, there was an error evaluating the direction of phase angle changes. It's possible \
        there is an error in the calculation between some of the times.")
        raise

    #If both angles are either both positive or both negative, their product will be positive.
    if (angle_changes[0]*angle_changes[1])>0:
        #If the triple product is +, angle_changes[2] must be +. So we have + + + or - - +
        if (angle_changes[0]*angle_changes[1]*angle_changes[2])>0:

            if angle_changes[1] >0:
                #thus it must be +++, phase angle is strictly increasing when angles[2] was measured
                 return "positive"
            else:
                #it's --+. Which implies the new moon occurs between angles[2] and angles[3]
                return "negative"

        #Ruling out --0. So we have + + - or - - - remaining
        else:
            if angle_changes[1]>0:
                #it's ++-. Which means the moon is near a full moon phase. So we just work backwards from angles[2]
                return "positive"
            else:
                #patently ---
                return "negative"

 #Ensuring product is negative. So we must have + - or - +
    else:
        #Positive triple product implies + - - or - + -
        #But - + - is not valid.
        if (angle_changes[0]*angle_changes[1]*angle_changes[2])>0:
            return "negative"

        #Negative triple product implies -++ or +-+.
        #Yet again, +-+ is not valid. So angles[2] must have been measured just after a new moon.
        elif angle_changes[2] !=0:
            return "positive"
            




