import copy
import math
import orbital
from functions      import *
from simulation     import Simulation
from vector3d       import Vector3D
# from params         import Params
from pyquaternion   import Quaternion
from keplerian      import keplerian_orbit, keplerian_elements
from earth          import Earth


class Trajectory(object):

    def __init__(self, rocket):

        self.rocket              = rocket
        self.params              = rocket.params
        self.pitchover           = self.params.trajectory_params['pitchover']
        self.rotation_axis       = self.calc_rotation_axis()
        self.intermediates       = int((self.pitchover[1]-self.pitchover[0]) * (1/self.params.timestep))
        self.max_iterations      = 50

        if self.params.optimized:
            self.pitchover_angle     = self.params.trajectory_params['pitchover_angle']
            self.coast_time          = self.params.trajectory_params['coast_time']
            self.calc_pitchover()
        else:
            self.pitchover_angle     = 0.0
            self.coast_time          = 5.0




    def calc_rotation_axis(self):

        q                        = Quaternion(axis=self.rocket.position.points, degrees=-self.params.launch_azimuth)
        v                        = self.rocket.velocity.points
        v_prime                  = q.rotate(v)

        return Vector3D(v_prime)




    def calc_pitchover(self):

        self.pitchover_maneuver  = []
        v                        = self.rocket.orientation.points
        q0                       = Quaternion(axis=self.rotation_axis.points, degrees=0.0)
        q1                       = Quaternion(axis=self.rotation_axis.points, degrees=-self.pitchover_angle)

        for q in Quaternion.intermediates(q0, q1, self.intermediates, include_endpoints=True):
            v_prime              = q.rotate(v)
            self.pitchover_maneuver.append(v_prime)






    def optimize_pitchover(self):

        injection                = orbital.utilities.radius_from_altitude( copy.copy(self.params.injection)*1000, body=orbital.earth)
        target_perigee           = injection
        target_apogee            = orbital.utilities.radius_from_altitude( copy.copy(self.params.apogee)*1000, body=orbital.earth)
        count                    = 0
        gain                     = 0.1
        tau_i                    = 0.01
        error                    = 1.0
        integral_error           = 0.0

        while abs(error) > math.pi * 0.5 * 0.001:

            self.calc_pitchover()
            rocket               = copy.deepcopy(self.rocket)
            simulation           = Simulation(rocket, self)
            simulation.run_simulation()

            k                    = keplerian_elements(rocket.position, rocket.velocity)
            apogee               = k[0]
            perigee              = k[1]
            peri_norm            = normalize(perigee, 0, target_perigee)
            apo_norm             = normalize(apogee, 0.0, target_apogee)
            apo_norm             = constrain(apo_norm, 0.0, 1.0)
            alt_norm             = normalize(rocket.position.magnitude(), 0.0, injection)

            # get the final injection angle
            horizontal           = math.pi * 0.5
            injection_angle      = simulation.rocket.position.angle(simulation.rocket.velocity)
            diff                 = horizontal - injection_angle                 # begins at 1.57 radian, approaches 0 when horizontal, goes negative if losing altitude
            diff_norm            = normalize(diff, 0.0, math.pi * 0.5)


            # if the rocket's injection altitude is greater than 130km, continue increasing the pitchover angle
            # so that it approaches a tangential injection angle
            if alt_norm >= 1.0:

                if apo_norm < 1.0:
                    error = -diff_norm
                else:
                    error = diff_norm

            # if the rocket's injection altitude is below 130km, this could be for a number of reasons
            else:

                # if the rocket's apogee doesn't reach the target, then the pitchover is too steep
                if apo_norm < 1.0:
                    error = -diff_norm

                # if the rocket's apogee reaches the target, then check to see what it's perigee is
                else:

                    # if the rocket's normalized perigee is greater than the normalized pitchover angle,
                    # then the pitchover angle is too steep
                    if peri_norm > diff_norm:
                        error = -diff_norm

                    # if the normalized pitchover angle is greater than the normalized perigee,
                    # then increasing the pitchover angle will raise the apogee
                    else:
                        error = diff_norm


            self.pitchover_angle += gain * error + tau_i * integral_error
            self.pitchover_angle = constrain(self.pitchover_angle, 0.0, 10.0)

            perigee                         = orbital.utilities.altitude_from_radius(perigee, body=orbital.earth)
            apogee                          = orbital.utilities.altitude_from_radius(apogee, body=orbital.earth)

            print("Error: %.2f, Pitchover: %.2f, apogee: %.2f, perigee: %.2f, altitude: %.2f, angle: %.2f" % \
                (error, self.pitchover_angle, apogee, perigee, rocket.altitude, injection_angle))

            count += 1

            if count > self.max_iterations:
                break




    def simulate(self):

        self.simulation          = Simulation(self.rocket, self)

        mdo                      = self.rocket.params.mdo
        output                   = self.rocket.params.output
        recover                  = self.rocket.params.recover
        circularize              = self.rocket.params.circularize
        geo                      = self.rocket.params.geo
        log                      = True

        self.simulation.run_simulation(mdo, log, output, recover, circularize, geo)


        if self.rocket.orbit     == True:
            prop_remaining       = sum([x.prop_mass for x in self.rocket.stages])
            result               = -self.rocket.payload + prop_remaining
        else:
            dv_remaining         = self.simulation.injection.velocity_perigee - self.rocket.velocity.magnitude()
            result               = self.rocket.payload + dv_remaining

        return result
