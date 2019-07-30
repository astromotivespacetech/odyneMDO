from math import pi, sqrt, pow, acos, degrees, radians
from constants import _u, J2
from earth import Earth






def sun_syncronous_inclination(altitude):

    Re  = Earth.radius_equator*0.001
    a   = altitude + Re                                 # semi-major axis
    i   = acos(-pow((a/12352), (7/2)))                  # inclination in radians

    return degrees(i)                                   # return inclination in degrees





if __name__ == "__main__":

    inc = sun_syncronous_inclination(500)
    print(inc)
