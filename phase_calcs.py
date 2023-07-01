import datetime
import numpy as np
import math
import itertools

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
    #If elapsed time is negative, we can find the phase by taking advantage of the cylical nature of the phases and incrementing by a period.
    #E.g. For Earth, the phase at 13 days from the next new moon is the same as one at -13 + 29.5 = 16.5 days after the next moon. 
    if elapsed_time < 0:
        elapsed_time = elapsed_time+moon_period

    _ , cycle_rem = divmod (elapsed_time, moon_period) 
    phase_index = math.floor((cycle_rem/moon_phase_length)) #Finds the 1/8th of the cycle the moon is in
    phase_name = moon_phases[phase_index]

    return phase_name


#FIND NEW MOON TIME. 
def calc_phase_zero_point(times, angles):
    times = [datetime.datetime.strptime(time_str, '%Y-%b-%d %H:%M') for time_str in times]
    # angles = [float(angle) for angle in angles]
    #Explicitly defining lengths for faster execution later.
    times_length = len(times)
    angles_length = len(angles)
    if (times_length<5) or (times_length!=angles_length):
        raise Exception("Raise exception")

#By multiplying the median, we get a selection criteria for points near the top of the phase curve.
    adj_angle_med = np.median(angles)*1.5

    #Need to filter a collection of points to perform the interpolation.
    #Ideally, we would like several points near the curve maximum to get a good polynomial.
    for i in range(1,angles_length-2):

        if angles[i] > adj_angle_med:

            elems_thereafter = angles[i:] #Find all points after i that are larger than criterion
            filtered_elems = list(itertools.takewhile(lambda x: x > adj_angle_med, elems_thereafter))
            num_filtered = len(filtered_elems)

            
            if num_filtered < 2:
                #When there is very few angle values near the minimum of the function, we need to at least include 1 point
                #before our target angle, and at least a couple afterwards. This is why the for loop starts at index 1 and not 0.
                start_index = i-1
                stop_index = i+1

            else:

                start_index = i
                stop_index = i+num_filtered
 
            break
    
    #Convert timestamps to numbers for interpolation
    rel_time_coords = [(times[i]-times[0]).total_seconds() for i in range(times_length)]

#Selection of points to be interpolated on
    interp_times = rel_time_coords[start_index:stop_index]
    interp_angles = angles[start_index:stop_index]

    from scipy.interpolate import InterpolatedUnivariateSpline
    f = InterpolatedUnivariateSpline(interp_times, interp_angles, k=4)

    #Subdivide interval for best accuracy in estimating the maximum
    finer_times = []
    for i in range(len(interp_times) - 1):
        start_time = interp_times[i]
        end_time = interp_times[i+1]
        sub_interval = (end_time - start_time) / 50 

    # Generate the additional time values within the subinterval
        for j in range(50):
            sub_time= start_time + (j * sub_interval)
            finer_times.append(sub_time)
    finer_times.append(interp_times[-1])

    #Find time at which phase curve interpolation peaks
    eval_vals= [f(i) for i in finer_times]
    max_ind = np.argmax(eval_vals)
    
    # import matplotlib.pyplot as plt
    #Interesting plots to look at phase angle shifts
    # plt.plot(times, angles)
    # plt.plot(times,[adj_angle_med for _ in times])
    # plt.plot(times[start_index:stop_index],y_vals, color="green")
    # plt.savefig("plots/a_vs_t.png")

    #Remember, finer_times is derived from interp_times, which itself is measured as time points since times[0]
    #Thus, we add interpolation time to times[0] to calculate the actual new moon timestamp

    new_moon_time = times[0]+datetime.timedelta(seconds = finer_times[max_ind])

    return new_moon_time






