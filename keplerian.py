import math
from constants import _u
from earth import Earth
from vector3d import Vector3D


def keplerian_orbit(position, velocity):

    # position magnitude
    r     = position.magnitude()

    # velocity magnitude
    v     = velocity.magnitude()

    # angular momentum pseudo-vector, cross product
    h_hat = position.cross(velocity)

    # angular momentum
    h     = h_hat.magnitude()

    # eccentricity vector
    e_hat = velocity.cross(h_hat)
    e_hat.divide(_u)
    e_hat.subtract(position.unit())

    # eccentricity
    e     = e_hat.magnitude()

    if e == 1:
        e = 1 - 1e-16

    # semi latus rectum
    p     = h ** 2 / _u

    # periapsis distance
    d_p   = p / (1 + e)

    # apoapsis distance
    d_a   = p / (1 - e)

    return d_p, d_a





if __name__ == "__main__":

    R_e     = Earth.radius_equator

    pos     = Vector3D([R_e + 200000, 0, 0])
    vel     = Vector3D([0, 7900, 0])

    k       = keplerian_orbit(pos, vel)

    print("PERIGEE: %f km, APOGEE: %f km" % ((k[0]-R_e)*0.001,(k[1]-R_e)*0.001))
