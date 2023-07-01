import requests
import json
import datetime
import re 
import numpy as np 
import math
from astroquery.jplhorizons import Horizons


#DATA NOTES
    #Alternative places to find satellite data:
    #NASA PDS dataset
    # https://pds.nasa.gov/ds-view/pds/viewTargetProfile.jsp?TARGET_NAME=GANYMEDE
    #Based off of Astrophysical Data I. Planets and Stars. Kenneth R. Lang 1992

    #Main NASA Horizons API(accessed through astroquery in our case)


    #Devstronomy has json and csv files that pairs moons with planets. Will try to replace this with something more comprehensive in the future.
    # https://github.com/devstronomy/nasa-data-scraper/blob/master/data/csv/satellites.csv


#RETURN MOON INFO
#  Returns planet_name for now, but functionality is extensible.
def grab_moon_info(moon_name):
   
    with open('satellites.json', 'r') as file:
    # Load the JSON data
        content  = json.load(file)
        id_dict = {1:"Mercury", 2:"Venus",3:"Earth", 4:"Mars", 5:"Jupiter", 6:"Saturn", 7:"Uranus", 8:"Neptune"}

      #next() and a generator reconstructs the necessary dictionary(better than a list comprehension!)
        target_content = next((item for item in content if item["name"]==moon_name), None)

        try:
            
            planet_id = target_content["planetId"]
            planet_name = id_dict[planet_id]
            
            #If the dictionary is inverted the other way around, i.e Planet_name : planet_id order 
            # planet_name = list(filter(lambda x:id_dict[x]==planet_id, id_dict))[0]
        except:
            raise Exception("""Something went wrong when trying to load in the moon data.
              Please double check your spelling of the moon name. Also, note the program only has support for 177 satellites listed in satellites.csv. \n""")

        #length of sidereal years given in days
        planet_year_dict = {"Mercury": 87.969257, "Venus":224.70079922 ,"Earth":365.25636,"Mars": 686.98, "Jupiter":4332.589, "Saturn":10755.698, "Uranus":30685.4, "Neptune": 60189}
        planetary_year = planet_year_dict[planet_name]

        return planet_name, planetary_year

#MAKE API CALL, RETURN DATA
def make_horizons_call(moon_name, planet_name,planetary_year, input_date):

    #Even though they have no moons, Mercury and Venus are included for future functionality.
    nasa_planet_codes = {"Mercury":"199","Venus":"299","Earth":"399", "Mars":"499", "Jupiter":"599", "Saturn":"699", "Uranus":"799","Neptune":"899"}

    #Edge cases is a bandaid fix for the Horizons API interpreting multiple possible names for a given moon name. 
    # e.g. Titan could be construed as just "Titan" or "Titania"
    #Will try to fully fix later by formatting id data in dumpdata.py

    edge_cases = {"Titan":"606", "Io":"501","Europa":"502", "Moon":"301"}
    if moon_name in edge_cases.keys():
        moon_id = edge_cases[moon_name]
    else:
        moon_id = moon_name

    start_time = input_date
    #A 14 day stretch of data should be enough to estimate phase angle change to a good degree(even for slow moons like Neso)
    stop_time = start_time + datetime.timedelta(days=1)
    init_start_time = start_time.strftime("%Y-%m-%d")
    init_stop_time = stop_time.strftime("%Y-%m-%d")


#Parameters defined in this fashion for the case a direct request to the NASA Horizons api is needed(not through astroquery.Horizons)
    parameters = {
        'COMMAND': moon_id,  
        'MAKE_EPHEM': 'YES',
        'VEC_CORR': 'NONE',
        "EPHEM_TYPE":'OBSERVER',
        "CENTER":"500@"+nasa_planet_codes[planet_name],
        "START_TIME":init_start_time,
        "STOP_TIME":init_stop_time,

        "STEP_SIZE": "3h",

    }


    #Unfortunately, the astroquery API call returns a list of different orbital periods which do not match the commonly accepted orbital period.
    #So we directly call the NASA API to get the single, commonly accepted orbital period

    #NASA API CALL AND REGULAR EXPRESSIONS
    main_url = "https://ssd.jpl.nasa.gov/api/horizons.api"

    r = requests.get(main_url,params=parameters)
    if r.status_code == 200:
        pass
    else:
        raise Exception("Error: could not make contact with the NASA JPL Horizons API.")

    content = r.text

    #NASA's API is inconsistent --so we have to try a few re matches

    attempt1 = re.search(r"(?i)orbital\s*period\s*(?:=)?\s*(?:~)?\s*[\d.]+\s*.", content)

    if attempt1: #Determine success of first match
        orbital_period_text = attempt1.group(0)

    else:
        #Attempt the second match
        attempt2 = re.search(r"(?i)orbit\s*period\s*(?:=)?\s*(?:~)?\s*[\d.]+\s*.", content)
        if not attempt2:
            raise Exception("Orbital period not found.")
 
        orbital_period_text= attempt2.group(0)


    #Split before 1st digit - removes '=', "~", etc.
    split_text = re.split(r'(?=\d)', orbital_period_text, 1)
    orbital_period_text = split_text[1]

    #Ensure Nasa's units are converted to days
    time_dict = {"h":1/24, "d": 1, "y":365.25}
    for key in time_dict.keys():
        #if moon_period is in h or y, iterating through the dict will allow us to convert to days
        if key in orbital_period_text:
            orbital_period_text=orbital_period_text.replace(key, "")
            moon_period = float(orbital_period_text)*time_dict[key]
            break

    #Nasa gives sidereal periods, so we have to quickly convert to synodic periods.
    synodic_inverse = abs(1 / planetary_year - 1 /moon_period)
    moon_period = 1 / synodic_inverse


    #We will use astroquery for the main API call as it returns neatly formatted data.
    #We will also now adjust the time parameters for the call. This ensures the moon phase 
    # calculator gets sufficient resolution of the phase angles across the moon's full cycle.
    #The orbital periods of moons vary from 7 hours(Metis) to 27 years(Neso). 
    # Thus, there isn't one stop_time and step_size configuration that works
    def scale_parameters(moon_period):

        moon_period_dt = datetime.timedelta(days=moon_period)
        moon_period_secs = moon_period_dt.total_seconds()

        start_time = datetime.datetime.strptime(parameters["START_TIME"], "%Y-%m-%d")
        stop_time = start_time+moon_period_dt
        stop_time = stop_time.strftime("%Y-%m-%d")
        step_size = moon_period_secs/100
        
        conv_unit_dict = {"y":31556952, "d":86400, "h":3600, "m":60}

        remainder = math.floor(step_size)

        #This is a repetitive division loop to find an ample step size.
        #Start with the highest time unit, see if at least 1 time unit fits the step size.
        #Otherwise, take the new remainder and divide it with the next largest time unit.
        for key, value in conv_unit_dict.items(): 
    
            divisor, remainder = divmod(remainder, value) 

            #Satisfy condition => break loop
            if divisor >= 1:
                step_size = math.floor(divisor)
                step_size = str(step_size)+key
               
                return stop_time, step_size


    parameters["STOP_TIME"], parameters["STEP_SIZE"] = scale_parameters(moon_period)
        
    #Actually make Astroquery API Call
    moon_obj = Horizons(id=moon_id, location=parameters["CENTER"],
                epochs={'start':parameters["START_TIME"], 'stop':parameters["STOP_TIME"],
                        'step':parameters["STEP_SIZE"]})

    ephems = moon_obj.ephemerides()
    ephem_data = np.array([ephems['datetime_str'], ephems["alpha_true"]])

    #Note ephems["alpha_true"] and ephems["alpha"] almost exactly the same

    #Dump data to pickles if API calls need to be reduced
    #import pickle
    # with open("phaseangle.pickle", "wb") as f:
    #     pickle.dump(data, f)
    # with open("phaseangle.pickle","rb") as f:
    #     data = pickle.load(f)

    return ephem_data , moon_period

#Test case for API call
# x,y = make_horizons_call("Ganymede", "Jupiter",4332, datetime.datetime.now())
# print(y)




        











