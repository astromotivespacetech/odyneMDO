import math
import orbital
from earth import Earth


def calc_distance_to_horizon(position):
    # http://www.ambrsoft.com/TrigoCalc/Circles2/CirclePoint/CirclePointDistance.htm

    lat     = Earth.get_lat_lon(position)[0]
    R       = Earth.radius_at_latitude(lat)
    xp      = position.magnitude()
    yp      = 0
    x1      = ( R**2 * xp + R * yp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    x2      = ( R**2 * xp - R * yp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    y1      = ( R**2 * yp - R * xp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    y2      = ( R**2 * yp + R * xp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    d       = math.sqrt( (xp - x1)**2 + (yp - y1)**2 )
    theta   = 2 * math.atan2(R, d)

    return d, theta



# print( math.degrees(theta), d )
