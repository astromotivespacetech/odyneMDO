from math           import pi
from vector3d       import Vector3D
from runge_kutta    import StateVector



class Fairing(object):

    mass            = 30.0      # [kg]
    residual_mass   = mass * 0.5
    diameter        = 1.05       # [m]
    length          = 1.7       # [m]
    jettison        = 100000.0   # [m]
    x_A             = 0.5 * pi * (diameter * 0.5)**2
    C_d             = 0.1

    # position and velocity states
    state           = StateVector(Vector3D([0,0,0]), Vector3D([0,0,0]))
    state_rel       = StateVector(Vector3D([0,0,0]), Vector3D([0,0,0]))

    # for simulation
    recovery_status = 1
