import copy
import math
import orbital
from functions      import *
from runge_kutta    import *
from units          import *
from constants      import g_earth, geostationary
from vector3d       import Vector3D
from earth          import Earth
from atmosphere     import Atmosphere
from orbit          import Orbit
from keplerian      import keplerian_orbit, keplerian_elements
from pyquaternion   import Quaternion
from dv             import calc_dv

earth = Earth()
atmosphere = Atmosphere()



class Simulation(object):

    def __init__(self, rocket, trajectory):

        self.rocket                     = rocket                                                            # rocket object
        self.params                     = rocket.params
        self.trajectory                 = trajectory                                                        # trajectory object
        self.dt                         = rocket.params.timestep                                            # 0.1 [s] forward increment

        # orbital elements
        self.injection                  = Orbit(kilo2unit(self.params.injection), kilo2unit(self.params.apogee))      # injection orbit object
        self.target_orbit               = Orbit(kilo2unit(self.params.perigee),   kilo2unit(self.params.apogee))      # target orbit object

        self.keplerian                  = keplerian_orbit(self.rocket.position, self.rocket.velocity)       # perigee and apogee velocity based on current state
        self.apogee                     = 0.0                                                               # tracks rocket apogee height
        self.calc_fuel_lox_resid()                                                                          # sets the residual fuel and lox mass for each stage
        self.circ_fuel, self.circ_lox   = self.calc_circularization_prop()                                  # required propellant to circularize at target orbit

        # launch sequence variables
        self.launch_sequence            = True
        self.stage_separation           = 1
        self.circ_burn                  = False
        self.fairing_status             = 1
        self.separation_sequence        = 0.0
        self.launch_hold                = [0.0, 1.0]
        self.liftoff                    = False
        self.stage                      = 0
        self.elapsed                    = 0.0
        self.geo_transfer               = False

        # forces
        self.acceleration               = Vector3D([0,0,0])
        self.drag                       = 0.0

        # other
        self.gravity_loss               = 0.0
        self.drag_loss                  = 0.0



    def calc_fuel_lox_resid(self):

        for i, stage in enumerate(self.rocket.stages):

            # compute fuel and oxidizer mass required for engine shutdown
            stage.fuel_shutdown = self.params.engine.Shutdown['Kerosene'] * len(stage.engines) * self.params.cores[i]
            stage.lox_shutdown  = self.params.engine.Shutdown['LOx']      * len(stage.engines) * self.params.cores[i]

            # compute residual mass in both tanks
            stage.fuel_resid    = sum([tank.fuel_mass_residual for tank in stage.tanks])
            stage.lox_resid     = sum([tank.lox_mass_residual  for tank in stage.tanks])



    def run_simulation(self, mdo=False, log=False, output=False, recover=False, circularize=False, geo=False):

        self.recover                    = recover
        self.log                        = log
        self.rocket.orbit               = False
        self.engine_startup_sequence()                                                                      # expends the necessary prop mass for current stage

        while self.check_launch_phase_status() == True:                                                     # do stuff while launching
            self.update_state()                                                                             # updates the rocket position, velocity state

        # returns True or False
        self.rocket.orbit   = self.check_orbit_status()                                                       # did it successfully reach orbit with enough remaining prop mass?

        # get first stage downrange distance
        if self.recover:
            stage           = self.rocket.stages[0]
            state_rel       = stage.state_rel.vector
            p_rel           = Vector3D([state_rel[0].p, state_rel[1].p, state_rel[2].p])
            stage.downrange = self.rocket.init_position.angle(p_rel) * Earth.radius_equator

        # continue simulating through circularization
        if self.rocket.orbit == True and circularize == True:

            # self.dt = 0.5

            # 90 minutes
            while self.check_circularization_status() == True:
                self.update_state()

                # self.keplerian                  = keplerian_orbit(self.rocket.position, self.rocket.velocity)
                # perigee                         = self.keplerian[0] - Earth.radius_equator
                # apogee                          = self.keplerian[1] - Earth.radius_equator

                # self.elements = keplerian_elements(self.rocket.position, self.rocket.velocity)



        if geo == True:

            # set geo_transfer to True
            self.geo_transfer = True

            # update stage with new params
            self.modified_third_stage()

            # new apogee
            self.params.perigee = geostationary
            self.params.apogee = geostationary
            self.target_orbit = Orbit(self.params.perigee, self.params.apogee)

            # geostationary transfer orbit burn
            while self.check_launch_phase_status() == True:
                self.update_state()

            # coast
            while self.check_circularization_status() == True:
                self.update_state()

            # circularize at apogee




        # display the simulation results in the console
        if output == True:

            stage = self.rocket.stages[self.stage]
            # print("Elapsed | Payload | PropMass | Alt | Vel | Angle | MR | Pitchover | Orbit")
            print("%.1f | %.1f | %.2f | %.1f | %.1f | %.1f | %.1f | %r | %r | %s" % \
                (round(self.elapsed, 1),
                self.rocket.payload,
                stage.prop_mass,
                self.circ_fuel + self.circ_lox + stage.fuel_resid + stage.lox_resid,
                self.rocket.altitude,
                self.rocket.velocity.magnitude(),
                math.degrees(self.rocket.position.angle(self.rocket.velocity_rel)),
                self.rocket.params.mass_ratios,
                [self.trajectory.pitchover_angle, self.trajectory.coast_time],
                self.rocket.orbit))




    def engine_startup_sequence(self):
        ''' Hadley engines have a startup sequence that requires chilling the turbopumps.'''

        stage                   =  self.rocket.stages[self.stage]
        en                      =  len(stage.engines)
        n2_tank                 =  stage.nitrogen_tank
        n2_tank.commodity_mass  -= self.params.engine.Chill['N2']       * en
        n2_tank.commodity_mass  -= self.params.engine.Start['N2']       * en
        n2_tank.update_mass()

        # subtract prop mass from tanks
        for tank in stage.tanks:
            tank.lox_mass       -= self.params.engine.Chill['LOx']      * en
            tank.fuel_mass      -= self.params.engine.Chill['Kerosene'] * en
            tank.lox_mass       -= self.params.engine.Start['LOx']      * en
            tank.fuel_mass      -= self.params.engine.Start['Kerosene'] * en

        stage.update_mass()
        self.rocket.mass        =  self.rocket.sum_stage_masses()




    def calc_thrust(self):
        ''' returns force as a scalar. Unit: [N] '''

        engines         = len(self.rocket.stages[self.stage].engines) * self.params.cores[self.stage]
        atm_p           = atmosphere.calc_ambient_pressure(self.rocket.altitude)
        atm_p_norm      = constrain_normalized(atm_p, 0.0, atmosphere.calc_ambient_pressure(0.0))
        if self.geo_transfer == True:
            thrust      = self.rocket.stages[self.stage].engines[0].thrust
        else:
            thrust      = engines * (self.params.engine.thrust['VAC'] - atm_p_norm * (self.params.engine.thrust['VAC'] - self.params.engine.thrust['SL']))

        return thrust




    def calc_accel(self):

        thrust          = self.calc_thrust() * self.rocket.stages[self.stage].throttle * self.stage_separation
        accel           = self.rocket.orientation.unit()
        accel.scale(thrust/self.rocket.mass)

        if self.rocket.altitude < 85000:
            self.drag   = atmosphere.calc_drag(self.rocket)
            drag        = self.rocket.velocity_rel.unit().inverse()
            drag.scale(self.drag/self.rocket.mass)
        else:
            drag        = Vector3D([0,0,0])
            self.drag   = 0.0

        g               = earth.calc_gravity(self.rocket.position.magnitude())
        gravity         = self.rocket.position.unit().inverse()
        gravity.scale(g)


        # calculate the component of thrust that is negated by gravity


        # # calculate the component of thrust that is vertical
        # theta           = self.rocket.position.angle(self.rocket.orientation) # radians
        # accel_vertical  = accel.magnitude() / math.cos(theta)
        #
        # # calculate the component of velocity that is horizontal
        # theta_2         = self.rocket.position.angle(self.rocket.velocity)
        # vel_horizontal  = self.rocket.velocity.magnitude() / math.sin(theta_2)
        #
        # # rocket angular velocity
        # omega           = vel_horizontal / self.rocket.position.magnitude()
        # c_f             = omega**2 * Earth.radius_equator
        #
        # # gravity losses equal gravitational acceleration while the vertical component of
        # # thrust is greater, otherwise gravity losses equal the vertical component of thrust
        # if accel_vertical >= g - c_f:
        #     self.gravity_loss += (g - c_f)                  * self.dt
        # else:
        #     self.gravity_loss += accel_vertical             * self.dt
        #
        # # drag losses equal drag acceleration
        # self.drag_loss        += self.drag/self.rocket.mass * self.dt


        acceleration    = Vector3D([0,0,0])
        acceleration.add(accel)
        acceleration.add(drag)
        acceleration.add(gravity)


        return acceleration



    def calc_component_accel(self, component):

        state                   = component.state.vector
        state_rel               = component.state_rel.vector
        component.position      = Vector3D([state[0].p, state[1].p, state[2].p])
        component.velocity      = Vector3D([state[0].v, state[1].v, state[2].v])
        component.position_rel  = Vector3D([state_rel[0].p, state_rel[1].p, state_rel[2].p])
        component.velocity_rel  = Vector3D([state_rel[0].v, state_rel[1].v, state_rel[2].v])

        pos                     = component.position.copy()
        vel                     = component.velocity.copy()
        speed                   = earth.surface_speed(pos)
        atm_vect                = Vector3D([-pos.y, pos.x, 0]).unit()
        atm_vect.scale(speed)
        vel.subtract(atm_vect)

        drag_force              = atmosphere.calc_drag(component)
        drag                    = vel.unit().inverse()
        drag.scale(drag_force/component.residual_mass)

        g                       = earth.calc_gravity(component.position.magnitude())
        gravity                 = component.position.unit().inverse()
        gravity.scale(g)

        acceleration            = Vector3D([0,0,0])

        if component.recovery_status == 1:
            acceleration.add(drag)
            acceleration.add(gravity)


        return acceleration




    def update_mass(self):

        stage                     = self.rocket.stages[self.stage]
        flow_rate                 = self.params.engine.flow_rate[self.params.performance] * len(stage.engines) * stage.throttle * self.dt * self.stage_separation

        if self.geo_transfer == True:
            m_dot_f               = self.rocket.stages[self.stage].engines[0].flow_rate['fuel'] * len(stage.engines) * stage.throttle * self.dt
            o_dot_f               = self.rocket.stages[self.stage].engines[0].flow_rate['ox']   * len(stage.engines) * stage.throttle * self.dt

        else:
            # Rocket propulsion elements pg 215
            m_dot_f               = flow_rate / (1 + self.params.engine.ox_f_ratio)
            o_dot_f               = flow_rate * self.params.engine.ox_f_ratio / (1 + self.params.engine.ox_f_ratio)

            # Nitrogen mass flow
            stage.nitrogen_tank.commodity_mass -= self.params.engine.IPS_purge[stage.nitrogen_tank.commodity.id] * len(stage.engines) * self.dt
            stage.nitrogen_tank.update_mass()

        for tank in stage.tanks:
            tank.fuel_mass        -= m_dot_f
            tank.lox_mass         -= o_dot_f

        # if altitude is above the specified fairing jettison, subtract the fairing mass
        # from this stage's dry mass, and then set the fairing mass to zero
        if self.rocket.altitude   >= self.rocket.fairing.jettison:
            stage.fairing_mass    -= self.rocket.fairing.mass * self.fairing_status
            self.fairing_status   = 0


        # update stage mass and rocket mass
        stage.update_mass()
        self.rocket.mass          = self.rocket.sum_stage_masses()




    def update_state(self):


        if self.launch_hold[0] < self.launch_hold[1]:
            self.launch_hold[0] += self.dt
        else:
            self.elapsed += self.dt
            self.update_rocket_orientation()

            # the acceleration that should always be applied to the second stage
            self.acceleration = self.calc_accel()

            if self.recover == True:

                # iterate over both stages
                for i, stage in enumerate(self.rocket.stages):

                    # if the current stage is the booster stage...
                    if self.stage == 0:

                        # apply the normal acceleration
                        accel = self.acceleration

                    # if the current stage is the second stage...
                    else:

                        # on the first iteration, calculate the BOOSTER acceleration
                        if i == 0:
                            accel = self.calc_component_accel(stage)

                        # otherwise, apply the normal acceleration
                        else:
                            accel = self.acceleration

                    # Current Stage: 1
                        # Iteration 1: apply normal accel to 1st stage
                        # Iteration 2: apply normal accel to 2nd stage
                    # Current Stage: 2
                        # Iteration 1: apply booster accel to 1st stage
                        # Iteration 2: apply normal accel to 2nd stage
                    self.apply_acceleration(stage, accel)

                # calculate acceleration for fairing if it is jettisoned
                if self.fairing_status == 0:
                    accel = self.calc_component_accel(self.rocket.fairing)
                # otherwise apply normal acceleration for fairing
                else:
                    accel = self.acceleration

                self.apply_acceleration(self.rocket.fairing, accel)

            else:
                self.apply_acceleration(self.rocket.stages[-1], self.acceleration)


        if self.stage_separation == 0:
            self.separation_sequence += self.dt
            if self.separation_sequence >= self.trajectory.coast_time:
                self.stage_separation = 1
                self.separation_sequence = 0.0

        self.update_mass()
        self.rocket.get_current_state()

        # # print seconds elapsed
        # if round(self.elapsed * 10) % 10 == 0:
        #     print(round(self.elapsed))

        if self.log:
            self.log_data()




    def apply_acceleration(self, stage, accel):

        # update position and velocity
        for s, a in zip(stage.state.vector, accel.points):
            rk4(s, a, self.dt)

        # update relative position and velocity
        for s, a in zip(stage.state_rel.vector, accel.points):
            rk4(s, a, self.dt)





    def update_rocket_orientation(self):

        if self.elapsed < self.rocket.trajectory.pitchover[0]:
            self.rocket.orientation = self.rocket.position.unit()

        elif self.elapsed >= self.rocket.trajectory.pitchover[0] and self.elapsed < self.rocket.trajectory.pitchover[1]:
            vector               = self.trajectory.pitchover_maneuver
            i                    = int((self.elapsed - self.rocket.trajectory.pitchover[0]) * (1/self.dt))
            self.rocket.orientation.update(vector[i])

        else:

            if self.rocket.orbit == True:
                self.rocket.orientation = self.rocket.velocity.unit()

            else:

                v_angle              = self.rocket.position.angle(self.rocket.velocity_rel)
                o_angle              = self.rocket.position.angle(self.rocket.orientation)

                if o_angle < v_angle:
                    if v_angle > math.radians(90.0):
                        d = v_angle - math.radians(90.0)
                        q = Quaternion(axis=self.trajectory.rotation_axis.points, degrees=math.degrees(d))
                        o = q.rotate(self.rocket.orientation.points)
                        self.rocket.orientation.update(o)
                    else:
                        self.rocket.orientation = self.rocket.velocity_rel.unit()




    def check_launch_phase_status(self):

        status                                          = True

        if self.recover == True:
            stage                                       = self.rocket.stages[0]
            if self.check_apogee()                      == True:
                if self.launch_sequence:
                    self.SECO()
                else:
                    pass
            else:
                self.check_stage_status()

            if self.launch_sequence                     == False:

                altitude_stage                          = Earth.get_lat_lon(stage.position)[2]
                altitude_fairing                        = Earth.get_lat_lon(self.rocket.fairing.position)[2]
                # print(altitude_stage, altitude_fairing)

                # check altitudes, set recovery status to zero if altitude is zero
                if round(altitude_stage) <= 0:
                    stage.recovery_status               = 0
                if round(altitude_fairing) <= 0:
                    self.rocket.fairing.recovery_status      = 0

                # if both stage and fairing altitudes are zero, then end
                if stage.recovery_status == 0 and self.rocket.fairing.recovery_status == 0:
                    status                              = False


        elif self.geo_transfer == True:
            if self.check_apogee() == True:
                status                                  = False
                self.rocket.stages[self.stage].throttle = 0.0
        else:
            if self.check_apogee() == True:             # True if current apogee is at least the target orbit altitude
                self.SECO()
                status                                  = False
            else:
                if self.check_stage_status() == True:
                    pass
                else:
                    status                              = False

        return status




    def calc_circularization_prop(self):

        # circularization dV
        circ_dV             = self.target_orbit.velocity_apogee - self.injection.velocity_apogee

        # increment size
        stepsize            = 0.1  # [kg]

        # last stage
        stage               = self.rocket.stages[-1]

        # dv = isp * g * log(m0 / mf)
        isp                 = self.params.engine.Isp['VAC'][self.params.performance]

        # compute startup propellant mass
        start_fuel          = self.params.engine.Start['Kerosene'] * len(stage.engines) * self.params.cores[-1]
        start_lox           = self.params.engine.Start['LOx']      * len(stage.engines) * self.params.cores[-1]

        circ_prop           = 0.0

        for i in range(3):

            # second stage dry mass plus residual propellant
            m0                  = stage.dry_mass + stage.fuel_resid + stage.lox_resid + circ_prop
            mf                  = m0
            dv                  = 0.0

            # iterate until dv is sufficient for circularization burn
            while dv < circ_dV:
                mf              -= stepsize                                         # de-increment initial mass to get final mass
                dv              = calc_dv(m0, mf, isp)                              # compute delta-v

            # different between initial mass and final mass is the propellant required for burn
            circ_prop = m0 - mf

        # compute fuel and lox mass from prop mass
        circ_fuel           = circ_prop / (1 + self.params.engine.ox_f_ratio)
        circ_lox            = circ_prop - circ_fuel
        circ_fuel           += start_fuel
        circ_lox            += start_lox

        return circ_fuel, circ_lox




    def check_apogee(self):

        self.keplerian                  = keplerian_orbit(self.rocket.position, self.rocket.velocity)
        perigee                         = self.keplerian[0]
        apogee                          = self.keplerian[1]


        # status
        target_apogee                   = orbital.utilities.radius_from_altitude( self.rocket.params.apogee*1000, body=orbital.earth)
        status                          = apogee >= target_apogee

        # if status:
        #     print("Apogee: %f, Perigee: %f" % (apogee, perigee))

        return status

        # update the target injection velocity based on current altitude, will start high and decrease,
        # as rocket velocity starts low and increases, they eventually converge at the injecton altitude
        # self.injection.update(self.rocket.altitude)
        #
        # return self.rocket.velocity.magnitude() > self.injection.velocity_perigee    # will return either true or false


    def check_orbit_status(self):

        status                              = self.check_apogee()

        if status:
            perigee                         = orbital.utilities.altitude_from_radius(self.keplerian[0], body=orbital.earth)
            apogee                          = orbital.utilities.altitude_from_radius(self.keplerian[1], body=orbital.earth)
            self.injection                  = Orbit(perigee, apogee)
            stage                           = self.rocket.stages[self.stage]
            fuel                            = sum([tank.fuel_mass for tank in stage.tanks])
            lox                             = sum([tank.lox_mass for tank in stage.tanks])
            self.circ_fuel, self.circ_lox   = self.calc_circularization_prop()

            if fuel > self.circ_fuel + stage.fuel_resid and lox > self.circ_lox + stage.lox_resid:                   # circ_fuel and circ_lox account for engine start quantities
                return True
            else:
                return False
        else:
            return False



    def check_stage_status(self):

        stage                               = self.rocket.stages[self.stage]

        # if on last stage, add circularization fuel and lox to residual
        if self.stage+1 == self.params.stages:
            fuel_resid                      = self.circ_fuel + stage.fuel_resid
            lox_resid                       = self.circ_lox  + stage.lox_resid
        else:
            fuel_resid                      = stage.fuel_resid + stage.fuel_shutdown
            lox_resid                       = stage.lox_resid  + stage.lox_shutdown


        # check mass in both fuel and oxidizer tanks, if either are less than the
        # computed residual mass
        if sum([tank.fuel_mass for tank in stage.tanks]) <= fuel_resid or sum([tank.lox_mass for tank in stage.tanks]) <= lox_resid:
            # if on last stage
            if self.stage+1 == self.params.stages:
                self.stage_separation = 0
                return False
            else:
                # increment stage and execute stage separation sequence
                self.stage += 1
                self.stage_separation = 0
                self.separate_stage()
                return True
        else:
            return True




    def separate_stage(self):

        stage                       = self.rocket.stages[0]
        state_rel                   = stage.state_rel.vector
        p_rel                       = Vector3D([state_rel[0].p, state_rel[1].p, state_rel[2].p])
        downrange                   = self.rocket.init_position.angle(p_rel) * Earth.radius_equator

        stage                       = self.rocket.stages[self.stage]
        prev_stage                  = self.rocket.stages[self.stage-1]

        # add fairing mass to successive stages, until fairing is jettisoned
        if self.fairing_status == 1:
            stage.fairing_mass      += self.rocket.fairing.mass * self.fairing_status
            prev_stage.fairing_mass -= self.rocket.fairing.mass * self.fairing_status

        # store final stage mass for further simulation
        prev_stage.residual_mass    = prev_stage.dry_mass + prev_stage.prop_mass

        # set previous stage and tank masses to zero so that rocket mass does not include it
        prev_stage.dry_mass         = 0.0
        prev_stage.prop_mass        = 0.0
        prev_stage.mass             = 0.0

        for tank in prev_stage.tanks:
            tank.fuel_mass          = 0.0
            tank.lox_mass           = 0.0

        # execute engine startup for current stage
        self.engine_startup_sequence()




    def SECO(self):

        stage                   =  self.rocket.stages[self.stage]

        # subtract nitrogen mass from tanks
        en                      =  len(stage.engines)
        n2_tank                 =  stage.nitrogen_tank
        n2_tank.commodity_mass  -= self.params.engine.Shutdown['N2']       * en
        n2_tank.update_mass()

        # subtract prop mass from tanks
        for tank in stage.tanks:
            tank.lox_mass       -= self.params.engine.Shutdown['LOx']      * en
            tank.fuel_mass      -= self.params.engine.Shutdown['Kerosene'] * en

        # coasting, so set throttle to zero
        stage.throttle          = 0.0

        stage.update_mass()
        self.rocket.mass        =  self.rocket.sum_stage_masses()
        self.launch_sequence    = False




    def check_circularization_status(self):

        status = True
        # print(self.rocket.velocity.magnitude())

        # start circularization burn once apogee is reached
        if self.rocket.altitude < self.apogee and self.circ_burn == False:
            self.rocket.stages[self.stage].throttle = self.rocket.params.throttle[self.stage]
            self.circ_burn = True
            self.target_orbit = Orbit(self.rocket.altitude, self.rocket.altitude)      # target orbit object


        # end circularization burn once desired velocity is attained
        if self.circ_burn == True and self.rocket.velocity.magnitude() >= self.target_orbit.velocity_apogee:
            self.rocket.stages[self.stage].throttle = 0.0
            self.circ_burn = -1
            # status = False
            # print(self.rocket.velocity.magnitude(), self.target_orbit.velocity_apogee)
            self.keplerian                  = keplerian_orbit(self.rocket.position, self.rocket.velocity)
            # print(self.rocket.altitude, self.keplerian[1] - Earth.radius_equator)

        if self.rocket.stages[self.stage].prop_mass <= 0.0:
            status = False

        if self.elapsed > self.params.duration:
            status = False

        self.apogee = self.rocket.altitude

        return status



    def log_data(self):

        self.rocket.flight_recorder.record_data(self.elapsed, self.acceleration, self.rocket, self.drag)
        # print(self.elapsed, self.keplerian[1] - Earth.radius_equator)



    def modified_third_stage(self):

        from R4D import R_4D
        from geo_transfer_mission import calc_geo_transfer

        stage = self.rocket.stages[self.stage]
        stage.engines = [R_4D]
        stage.nitrogen_tank.commodity_mass = 0.0
        stage.nitrogen_tank.dry_mass = 0.0
        stage.nitrogen_tank.mass = 0.0
        for x in stage.helium_tanks:
            x.dry_mass = 0.0
            x.commodity_mass = 0.0
            x.mass = 0.0
        stage.payload = 25.0
        stage.tank.dry_mass,  stage.tanks[0].fuel_mass, stage.tanks[0].lox_mass = calc_geo_transfer()
        stage.update_mass()
        stage.throttle = 1.0


# end
