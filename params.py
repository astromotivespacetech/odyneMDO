from units                  import *
from engine                 import Hadley
from fairing                import Fairing
from interstage             import Interstage
from tanks                  import HeliumTank, NitrogenTank
from parachute              import Parachute
from azimuth                import calc_launch_azimuth
from sun_syncronous         import sun_syncronous_inclination
from rotation_matrix        import rotation_angle
from commodities.aluminum   import Aluminum



class Params(object):

    # mdo params
    mdo_ratios              = [16.5, 6.5]
    mdo_payload             = 50.0     # [kg]

    # Rocket params
    stages                  = 2
    diameter                = 1.05      # [m]
    thrust_GTOW             = 1.2
    mass_ratios             = [16.485540238212664,  6.494060087323651]
    payload                 = 124.50402725306657   # [kg]

    # Stage params
    engine                  = Hadley
    engines                 = [4, 1]
    throttle                = [1.0, 0.7]
    cores                   = [1, 1]

    # interstage
    interstage              = Interstage

    # Fairing params
    fairing                 = Fairing

    # Recovery params
    recovery = {
        'ballute'           : 5, # [kg]
        'parachute'         : Parachute().mass, # [kg]
        'drogues'           : 2  # [kg]
    }


    # Engine params
    performance             = 'high'

    # tank params
    tank_caps               = 0.32       # [m]
    material                = Aluminum
    tank_pressure           = psi2pascal(50.0)
    ullage                  = {'fuel': 0.95, 'oxidizer': 0.99}       # tank fill percentage
    tank_piping             = 1.05       # add five percent to tank mass for piping
    expulsion_efficiency    = 0.991       # percentage of propellant used for propulsion - Rocket Propulsion Elements pg 202-203

    # helium pressure vessel
    helium_tank             = HeliumTank
    tanks_per_stage         = [2, 1]

    # nitrogen tank
    nitrogen_tank           = NitrogenTank

    # Simulation params
    timestep                = 0.1  # [s]
    duration                = 6000 # [s] how long to run the simulation
    theta                   = rotation_angle(timestep)
    mdo                     = True
    output                  = True
    recover                 = False
    circularize             = True
    geo                     = False
    sso                     = True

    # Launch site
    launch_site             = 'psc-kodiak'

    # Launch site params [lat, lon, altitude, pitchover, max payload]
    coordinates = {
        'ksc-lp39a'         : [28.60785665, -80.60427205,    4.0],
        'psc-kodiak'        : [57.43498194, -152.34169916,  30.0, 0.7950279674847444],
        'vandenberg'        : [34.73447732, -120.59637824,  88.0],
        'camden'            : [30.95389287, -81.53155851,    6.0, 1.243825254857131, 121.5],
        'baikonur'          : [45.92030866,  63.34220224,  105.0],
        'omelek'            : [9.04815811,   167.74331356,   7.0],
        'hawaii'            : [19.670,      -154.984,        7.0, 1.2668355696867248, 125.7],
        'new-zealand'       : [-39.2615451,  177.86515609, 106.0],
        'french-guiana'     : [5.28740673,  -52.59197579,    5.0],
        'alcantara'         : [-2.31738967, -44.36801459,    1.0, 1.2895154691987594, 190.0],
        'mid-atlantic-lp0a' : [37.83393787, -75.48771441,    1.0],
        'mid-atlantic-lp0b' : [37.8311811,  -75.49133277,    1.0, 1.2642700281640897, 155.5],
    }

    # Trajectory params
    latitude                = coordinates[launch_site][0]
    longitude               = coordinates[launch_site][1]
    altitude                = coordinates[launch_site][2]
    pitchover_angle         = coordinates[launch_site][3] if len(coordinates[launch_site]) > 3 else 1.0
    max_payload             = coordinates[launch_site][4] if len(coordinates[launch_site]) > 4 else payload    # [kg]
    direction               = 'south'
    injection               = 130 # [km]
    apogee                  = 500 # [km]
    perigee                 = 500 # [km]
    inclination             = sun_syncronous_inclination(apogee) if sso == True else 90.0
    launch_azimuth          = calc_launch_azimuth(latitude, inclination, injection, apogee, direction) # [deg]
    optimized               = True
    trajectory_params = {
        'pitchover_angle'   : pitchover_angle,      # [deg]
        'coast_time'        : 5.0,                  # [s]
        'pitchover'         : [10.0, 25.0]          # [s] T+ start / end pitchover
    }
