from fractions import Fraction
import math
    
#CALCULATE METONIC CYCLE BY MATCHING PLANET YEARS AND MOON PERIODS
def metonic_cycle_calc(sync_error, planetary_year, moon_period):
    #using earth years
    raw_ratio = planetary_year/moon_period
    approx_ratio = math.floor(raw_ratio)
    approx_coeffs = [approx_ratio]
    
    ratio_of_rem = 1/(raw_ratio - approx_ratio)


    for _ in range(100):
        approx_ratio = math.floor(ratio_of_rem)
        approx_coeffs.append(approx_ratio)

        #Need to convert reverse generator to list in order to measure its length
        frac_rep = get_abs_frac(list(reversed(approx_coeffs)))

        # print(frac_rep)
        approx_planet_years = frac_rep.denominator
        approx_moon_periods = frac_rep.numerator
        # print(approx_planet_years)
        # print(approx_moon_periods)
        error = approx_planet_years*planetary_year - approx_moon_periods*moon_period
        error = abs(error)
  

        if error < sync_error: 

            return [approx_planet_years, approx_moon_periods, error]

        ratio_of_rem = 1/(ratio_of_rem-approx_ratio)
        # print(ratio_of_rem)
    raise Exception("After 100 approximations of planet-moon period ratios, the program could not find a metonic cycle accurate enough for your error specification. \
                    Please consider raising the error threshold ")





#Calculates recursive fraction as a simplified improper fraction.

#Finding the simplified fraction of a complex fraction requires working backwards.
#Say you have 1+1/(2+(1/2)). Then you first turn 2+1/2 into an improper fraction by having 2=4/2, 4/2+1/2 --> 5/2. 
#For our case, we take advantage of "1" always being the numerator above the denominator that is coeff_list[0]
#Then, it has to be flipped(hence denominator/numerator interchange)
def get_abs_frac(coeff_list):

#The first set of operations to recursively evaluate a nested fraction are very important.
#To start the recursion, we evaluate two of the nested fraction coefficients at once; 
# This creates a partial frac term that we further sequentially calculate by only added ONE coefficient at a time.

    list_size = len(coeff_list) 
    partial_frac = Fraction(int(coeff_list[0] * coeff_list[1] + 1), coeff_list[0])

#Starting case
    if list_size==2:
        return partial_frac

#For 3+ coefficients we always flip the fraction and remove coefficients. However, if we start at list_size=3, we immediately add the last coefficient in the list
#as a consequence of us having to delete 2 coefficients in starting the recursion.

    partial_frac = Fraction(partial_frac.denominator, partial_frac.numerator)
    del coeff_list[0:2] #del over slice for speed :)

    if list_size ==3:
        partial_frac = Fraction(coeff_list[0],1)+partial_frac
        return partial_frac
    
    #We mutate list_size into a new counter variable, depth.
    depth = list_size-1

    while depth > 2:
        partial_frac = Fraction(coeff_list[0],1)+partial_frac
        partial_frac = Fraction(partial_frac.denominator, partial_frac.numerator)
        del coeff_list[0]
        depth -=1
 

    partial_frac = Fraction(coeff_list[0],1)+partial_frac
    return partial_frac


#Calculate absolute decimal value of a recursive fraction
def calc_recursive_frac(coeff_list):
    depth = len(coeff_list)-1

    x1= coeff_list[0]
    x2 = coeff_list[1]


    if depth == 1:
        return x1 +1/x2
    else:
        coeff_list.pop(0)
        return x1 + 1 / (x2 + calc_recursive_frac(coeff_list))

