import math
import orbital
from earth import Earth
from vector3d       import Vector3D


def calc_distance_to_horizon(position, angle):
    # http://www.ambrsoft.com/TrigoCalc/Circles2/CirclePoint/CirclePointDistance.htm

    lat     = Earth.get_lat_lon(position)[0]
    R       = Earth.radius_at_latitude(lat)

    # position
    xp      = position.magnitude()
    yp      = 0

    # tangent points on circle
    x1      = ( R**2 * xp + R * yp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    x2      = ( R**2 * xp - R * yp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    y1      = ( R**2 * yp - R * xp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)
    y2      = ( R**2 * yp + R * xp * math.sqrt(xp**2 + yp**2 - R**2) ) / (xp**2 + yp**2)

    # distance from position to tangent points
    d       = math.sqrt( (xp - x1)**2 + (yp - y1)**2 )

    # angle between tangent points on circle
    theta   = 2 * math.atan2(R, d)

    # rotate first tangent point to get new point on circle
    _0      = math.radians( angle )
    xprime  = x1 * math.cos(_0) - y1 * math.sin(_0)
    yprime  = x1 * math.sin(_0) + y1 * math.cos(_0)

    # rotate vector for new point by 90 degrees
    tangent     = [xprime * math.cos(math.radians(-90)) - yprime * math.sin(math.radians(-90)), xprime * math.sin(math.radians(-90)) + yprime * math.cos(math.radians(-90))]

    # get vector from new point on circle and original position
    new         = [xprime - xp, yprime - yp]

    # angle between tangent and new
    dot         = tangent[0] * new[0] + tangent[1] * new[1]
    m1          = math.sqrt(tangent[0]**2 + tangent[1]**2)
    m2          = math.sqrt(new[0]**2 + new[1]**2)
    if dot / (m1 * m2) > 1.0:
        n   = 1.0
    elif dot / (m1 * m2) < -1.0:
        n   = -1.0
    else:
        n   = dot / (m1 * m2)
    angle       = math.acos( n )

    # angle between original position and new
    dot         = -xp * new[0] + -yp * new[1]
    m1          = math.sqrt(xp**2 + yp**2)
    m2          = math.sqrt(new[0]**2 + new[1]**2)
    if dot / (m1 * m2) > 1.0:
        n   = 1.0
    elif dot / (m1 * m2) < -1.0:
        n   = -1.0
    else:
        n   = dot / (m1 * m2)
    _0      = math.acos( n )


    return d, theta, xprime, yprime, angle, m2, new, _0


if __name__ == "__main__":

    ang      = 0
    int      = 0
    prev     = 0

    pos      = Vector3D([0,Earth.radius_equator+500000,0])
    d, theta, x, y, angle, m, new, _0 = calc_distance_to_horizon(pos, ang)

    KP = 0.25
    KI = 0.0
    KD = 0.0

    err = 15 - math.degrees(angle)
    int += err
    ang += KP * err + KI * int + KD * prev
    prev = err - prev

    print(math.degrees(angle), ang)

    while abs(err) > 1e-4:
        d, theta, x, y, angle, m, new, _0 = calc_distance_to_horizon(pos, ang )

        err = 15 - math.degrees(angle)
        int += err
        ang += KP * err + KI * int + KD * prev
        prev = err - prev

        print(math.degrees(angle), ang)

    print(math.degrees(theta/2), math.degrees(_0))



    # print( math.degrees(theta), d )
