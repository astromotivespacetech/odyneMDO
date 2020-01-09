import math
import orbital
from constants import _u
from earth import Earth
from vector3d import Vector3D

def keplerian_elements(position, velocity):

    x = position.x
    y = position.y
    z = position.z
    vx = velocity.x
    vy = velocity.y
    vz = velocity.z

    r = orbital.utilities.Position(x,y,z)
    v = orbital.utilities.Velocity(vx,vy,vz)

    keplerian = orbital.elements.KeplerianElements.from_state_vector(r, v, body=orbital.earth)

    A = keplerian.a * (1 + keplerian.e)
    P = keplerian.a * (1 - keplerian.e)
    alt = orbital.utilities.altitude_from_radius(position.magnitude(), body=orbital.earth)

    return A, P, alt


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
