from math import sin, radians, degrees
from vector3d import Vector3D
from pyquaternion   import Quaternion


def moment_of_inertia(m, r, h):
    ''' Calculates rocket moment of inertia. Simplifying assumption is
        a solid cylinder.

        Arguments:
            m: mass [kg]
            r: radius [m]
            h: height [m]

        Returns: Moment of Inertia '[kg m^2]'
    '''

    return 1/12 * m * (3 * r ** 2 + h ** 2)



def torque(F, r):
    ''' Calculates torque on rocket from gimbaling engines.

        Arguments:
            F: total engine force [N]
            r: vector from axis of rotation to application of force [m]

        Returns: Torque vector [N]
    '''

    return F.cross(r)




def angular_accel(t, I):
    ''' Angular acceleration given torque and moment of inertiaself.

        Arguments:
            t: torque [N*m]
            I: moment of inertia

        Returns: Angular acceleration '[rad/s^2]'
    '''

    return t / I






if __name__ == "__main__":

    dt = 0.1            # [s]

    mass   = 7200.0    # [kg]
    radius = 0.525      # [m]
    height = 11.6       # [m]
    I      = moment_of_inertia(mass, radius, height)

    cg     = height/2   # center of gravity
    thrust = 88800      # [N]
    gimbal = 0.5        # [deg]

    angular_momentum = Vector3D([0,0,0])
    angular_velocity = Vector3D([0,0,0])


    # Represent initial orientation in body space as a unit vector in the Z direction
    orientation = Vector3D([0,0,1])

    # A unit Quaternion that will represent the current orientation as rotation applied
    # to the initial orientation vector
    Q_orientation = Quaternion(1, 0, 0, 0)


    # Iterate forward 10 steps
    for x in range(10):

        # The thrust vector depends on the rocket's orientation since the engines are mounted
        # to the rocket, so we create
        thrust_vector = Vector3D(Q_orientation.rotate(orientation.points))
        thrust_vector.scale(thrust)

        # The engines can be gimballed around any axis that is orthagonal to the thrust vector.
        # In this case, a unit vector along the x axis will always be valid
        rotation_axis = Vector3D([0, 1, 0])
        Q_gimbal = Quaternion(axis=rotation_axis.points, degrees=gimbal)
        thrust_vector = Vector3D(Q_gimbal.rotate(thrust_vector.points))

        # A vector pointing from the origin (center of gravity) to the point where the
        # force is applied
        force = Vector3D(Q_orientation.rotate(orientation.points))
        force.scale(cg)

        torque = torque(thrust_vector, force)
        torque.scale(dt)

        angular_momentum.add(torque)

        angular_vel = angular_momentum.copy()

        angular_vel.scale(1/I)

        angular_velocity.add(angular_vel)

        Q_angular_velocity = Quaternion(scalar=None, vector=angular_velocity.points)

        Q_spin = 0.5 * Q_orientation * Q_angular_velocity

        Q_orientation = Q_orientation + Q_spin

        Q_orientation = Q_orientation.unit

        print( Q_orientation.rotate(orientation.points) )







    # t      = torque(thrust, radians(gimbal), cg)
    # a      = angular_accel(t[0], I[0])
    #
    # print("\nMoment of inertia: %f %s\nTorque: %f %s\nAngular acceleration: %f %s\n" % (I[0], I[1], t[0], t[1], a[0], a[1]) )
