"""
Module for assessing skiing conditions based on WRF model parameters.

Author
------
Joep van Noort

Functions
---------
1. `mountain_check(lon, lat, ds)`: 
    Estimates whether a given location is of sufficient altitude for reliable snow cover during the Northern Hemisphere Winter.
    Returns minimum_mountain_height, topographic_height, snowsure, skiing_slope.

2. `snow_variables(lon, lat, ds, time=24)`: 
    Assesses meteorological conditions for skiing at a given location based on WRF parameters such as snowfall, sunshine, and wind.
    Returns snowcover, snowfall, sun, wind.

Dependencies
------------
- numpy as np
- wrfvis.grid

Usage
-----
1. Import the module: `import wrfvis.snowcheck`.
2. Call the desired functions based on skiing condition assessments.
3. Ensure that the required dependencies are installed before using the module.
"""

import numpy as np
from wrfvis import grid

def mountain_check(lon, lat, ds):
    """
    @author: Joep van Noort

    This function uses the WRF topographic model and a latitude value to
    estimate whether a given location is of sufficient altitude to have
    a reliable snowcover during the Northern Hemisphere Winter.

    The linear function relating winter snowcover and latitude is based on
    Saavedra (2018), Hantel et al. (2012) and ski resort base heights in Spain
    and Austria with a range of latitudes between 37ºN and 48ºN.

    It also checks if there are sufficient height differences in the gricell.
    Using the Slope variable from the WRF output, it was found that a value
    of 0.018 represents a representative cutoff between areas that are too
    flat and areas that have adequate slopes. 

    Parameters
    ----------
    lon : user input longitude value in degrees East
    lat : user input latitude value in degrees North
    ds : wrfout dataset

    Returns
    -------
    minimum_mountain_height : height at which a location of given latitude
                              is expected to be snowsure in NH winter.
    topographic_height : model height of given location according to WRF.
    snowsure : int 4 if topographic_height > minimum_mountain_height, else 0
    skiing_slope : int, 4 if model Slope variable is > 0.018
    """
    # Use linear function to obtain a minimum snowsure height based on latitude
    minimum_mountain_height = 3200 - (lat-30) * 125
    if minimum_mountain_height < 0:
        minimum_mountain_height = 0

    # For input location, obtain gridcell index and distance from center
    ngcind, ngcdist = grid.find_nearest_gridcell(
                      ds.XLONG[0, :, :], ds.XLAT[0, :, :], lon, lat)

    # Use WRF HGT parameter to obtain model height of gridcell
    topographic_height = ds['HGT'][0, ngcind[0], ngcind[1]].values

    # Compare topographic height and minimum snowsure height. Also check slope
    # angle
    if topographic_height > minimum_mountain_height:
        snowsure = 'Yes'
        # obtain slope value from WRF SLOPE paramter
        slope = ds['SLOPE'][0, ngcind[0], ngcind[1]].values
        if slope > 0.018:
            skiing_slope = 'Yes'
        else:
            skiing_slope = 'No'
    else:
        snowsure = 'No'
        slope = ds['SLOPE'][0, ngcind[0], ngcind[1]].values
        if slope > 0.018:
            skiing_slope = 'Yes'
        else:
            skiing_slope = 'No'
    # format the strings including mountain height and topographic height
    minimum_mountain_height_value = f'{minimum_mountain_height:,.0f} meters'
    topographic_height_value = f'{topographic_height:,.0f} meters'

    return (minimum_mountain_height, topographic_height,
            minimum_mountain_height_value, topographic_height_value,
            snowsure, skiing_slope)


def snow_variables(lon, lat, ds, time=24):
    """
    @author: Joep van Noort

    This function uses WRF parameters to assess the meteorological conditions
    for a given location with skiing in mind. Snowfall, sunshine and wind are
    considered.

    Values of 0-4 are given to enable coloring in html tables used for 
    output of these parameters. 

    Parameters
    ----------
    lon : user input longitude value in degrees East
    lat : user input latitude value in degrees North
    ds : wrfout dataset
    time : WRF timestep (0-35). Default 24h

    Returns
    -------
    snowcover : 4 if there is snowcover according to the model,
                0 if there is no snowcover.
    snowfall : accumulated snowfall over the next (time) hours. Gets a value
               according to the total amount. More is better (higher score)
    sun : sunshine score from 0 to 4 determined by cloud fraction at a
          particular location, less clouds are better (higher score)
    wind : windspeed is calculated from U and V components, modelled at 10m.
           wind is then given a score from 0 to 4, less wind is better. It is
           based on the Beaufort scale.
    """
    # For input location, obtain gridcell index and distance from center
    ngcind, ngcdist = grid.find_nearest_gridcell(
                      ds.XLONG[0, :, :], ds.XLAT[0, :, :], lon, lat)

    # set snowcover_value to 'None'
    snowcover_value = 'None'
    # obtain snowcover variable value from WRF SNOWC parameter
    snowcover = ds['SNOWC'][time, ngcind[0], ngcind[1]].values
    if snowcover == 0:
        snowcover = 0
    else:
        snowcover = 4
        snowcover_value = 'Yes'
        
    # Set Snowfall to 0, changes only if accumulated snowfall is predicted
    snowfall = 0
    snowfall_value = 'None :('
    # Obtain accumulated snowfall from WRF SNOWNC parameter.
    accumulated_snowfall = ds['SNOWNC'][time, ngcind[0], ngcind[1]].values
    if np.any(accumulated_snowfall > 0) and np.all(accumulated_snowfall < 5):
        snowfall = 1
        snowfall_value = '0-5 cm'
    elif (np.any(accumulated_snowfall >= 5)
          and np.all(accumulated_snowfall < 15)):
        snowfall = 2
        snowfall_value = '5-15 cm'
    elif (np.any(accumulated_snowfall >= 15)
          and np.all(accumulated_snowfall < 30)):
        snowfall = 3
        snowfall_value = '15-30 cm'
    elif np.any(accumulated_snowfall >= 30):
        snowfall = 4
        snowfall_value = '>30 cm :D'

    # Set Sun to 4, change if clouds are predicted
    sun = 4
    sun_value = 'Sunny'
    # Obtain cloud fraction from WRF CLDFRA parameter.
    cloud_fraction = ds['CLDFRA'][time, np.arange(77), ngcind[0],
                                  ngcind[1]].values
    if np.any(cloud_fraction > 0.05) and np.all(cloud_fraction < 0.1):
        sun = 3
        sun_value = 'Mostly Sunny'
    elif np.any(cloud_fraction >= 0.1) and np.all(cloud_fraction < 0.4):
        sun = 2
        sun_value = 'Somewhat Sunny'
    elif np.any(cloud_fraction >= 0.4) and np.all(cloud_fraction < 0.8):
        sun = 1
        sun_value = 'Mostly Cloudy'
    elif np.any(cloud_fraction >= 0.8):
        sun = 0
        sun_value = 'Overcast'

    # set wind value to 4, change if windspeed is >1 m/s
    wind = 4
    # calculate winspeed as the sum of U and V wind vectors.
    wind_U = ds['U10'][time, ngcind[0], ngcind[1]].values
    wind_V = ds['V10'][time, ngcind[0], ngcind[1]].values
    windspeed = np.sqrt((wind_U)**2+(wind_V)**2)
    if windspeed > 1 and windspeed < 3:
        wind = 3
    elif windspeed >= 3 and windspeed < 8:
        wind = 2
    elif windspeed >= 8 and windspeed < 15:
        wind = 1
    elif windspeed >= 15:
        wind = 0
    wind_value = f'{windspeed:,.2f} m/s'

    return (snowcover, snowcover_value, snowfall, snowfall_value, sun,
            sun_value, wind, wind_value)
