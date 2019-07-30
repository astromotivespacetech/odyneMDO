'''
An implementation of Runge-Kutta 4th order numerical integration, to estimate
position and velocity with respect to time and given acceleration. In this
example, acceleration is constant as only gravity is accounted for, but can
be varied as a function of force and mass.
'''

from vector3d import Vector3D



class State(object):

    def __init__(self, x = 0.0, v = 0.0):
        self.p  = x  # position
        self.v  = v  # velocity



class StateVector(object):

    def __init__(self, position, velocity):
        self.vector = [State(p, v) for p, v in zip(position.points, velocity.points)]



class Derivative(object):

    def __init__(self, dp = 0.0, dv = 0.0):
        self.dp = dp    # velocity
        self.dv = dv    # acceleration



def eval(initial, accel, dt, d):

    state     = State()
    state.p   = initial.p + d.dp * dt
    state.v   = initial.v + d.dv * dt

    output    = Derivative()
    output.dp = state.v
    output.dv = accel

    return output



def rk4(state, dv, dt):
    ''' Implements Runge-Kutta 4th order numerical integration.  '''

    k1      = eval(state, dv, dt, Derivative())
    k2      = eval(state, dv, dt*0.5, k1)
    k3      = eval(state, dv, dt*0.5, k2)
    k4      = eval(state, dv, dt, k3)

    dpdt    = ( k1.dp + 2.0 * ( k2.dp + k3.dp ) + k4.dp ) / 6.0
    dvdt    = ( k1.dv + 2.0 * ( k2.dv + k3.dv ) + k4.dv ) / 6.0

    state.p += dpdt * dt
    state.v += dvdt * dt




if __name__ == '__main__':

    # initial params
    timestep     = 0.1 # [ms]
    duration     = 1.0 # [s]

    position     = Vector3D([0.0, 9.8, 0.0])
    velocity     = Vector3D([0.0, 0.0, 0.0])
    acceleration = Vector3D([0.0,-9.8, 0.0])

    state = StateVector(position, velocity)

    # numerical integration loop
    for x in range( int(duration/timestep) ):
        #
        # could implement a function to vary acceleration here
        #
        for s, a in zip(state.vector, acceleration.points):
            rk4(s, a, timestep)



    # print results
    print('X Position: %r m, X Velocity: %r m/s after %i second(s)' % (state.vector[0].p, state.vector[0].v, duration))
    print('Y Position: %r m, Y Velocity: %r m/s after %i second(s)' % (state.vector[1].p, state.vector[1].v, duration))
    print('Z Position: %r m, Z Velocity: %r m/s after %i second(s)' % (state.vector[2].p, state.vector[2].v, duration))
