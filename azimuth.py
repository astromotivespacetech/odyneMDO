from math import sin, cos, asin, atan2, degrees, radians
from orbit import Orbit


def calc_launch_azimuth(latitude, inclination, injection, apogee, dir):
    ''' Calculates launch azimuth for a desired orbit from a launch latitude.
        Source: https://www.orbiterwiki.org/wiki/Launch_Azimuth

        Arguments:
            latitude [deg].
            inclination [deg].
            injecton [km].
            apogee [km].
            dir: launching north or south.

        Returns:
            launch azimuth angle [deg].
    '''

    orbit       = Orbit(injection*1000, apogee*1000)
    _0          = cos(radians(latitude))
    i           = cos(radians(inclination))
    B           = asin(i/_0)

    v_orbit     = orbit.velocity_perigee
    v_eqrot     = 465.1 #[m/s]
    v_xrot      = v_orbit * sin(B) - v_eqrot * cos(radians(latitude))
    v_yrot      = v_orbit * cos(B)

    B_rot       = degrees(atan2(v_xrot,v_yrot))

    if dir == 'north':
        return B_rot
    else:
        return 180 - B_rot
