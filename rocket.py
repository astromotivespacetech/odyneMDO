import math
import copy
import orbital
from constants          import g_earth
from functions          import tabs
from params             import Params
from stage              import Stage
from vector3d           import Vector3D
from runge_kutta        import StateVector
from earth              import Earth
from atmosphere         import Atmosphere
from simulation         import Simulation
from trajectory         import Trajectory
from flight_recorder    import FlightRecorder
from visualization      import Render3D
from dv                 import calc_dv

class Rocket(object):


    def __init__(self, params):

        # rocket attributes
        self.params             = params
        self.payload            = params.payload
        self.diameter           = params.diameter

        # position and velocity
        self.position           = Earth.get_cartesian(params.latitude, params.longitude, params.altitude)
        self.position_rel       = self.position.copy()
        self.velocity           = self.calc_initial_velocity(params.latitude)
        self.velocity_rel       = Vector3D([0,0,0])
        self.init_position      = self.position.copy()

        # fairing
        self.fairing            = params.fairing
        self.fairing.state      = StateVector(self.position, self.velocity)
        self.fairing.state_rel  = StateVector(self.position_rel, self.velocity_rel)

        # stages
        self.stages             = [Stage(x, self) for x in range(params.stages)]
        self.mass               = self.sum_stage_masses()
        self.height             = sum([x.height for x in self.stages])
        self.thrust_GTOW        = self.stages[0].thrust / (self.mass * g_earth)
        self.x_A                = math.pi * (0.5 * self.fairing.diameter) ** 2
        self.C_d                = 0.26

        # orientation and altitude
        self.orientation        = self.position.unit()
        self.altitude           = Earth.get_lat_lon(self.position)[2]
        self.downrange          = self.init_position.angle(self.position_rel) * Earth.radius_equator
        self.trajectory         = Trajectory(self)

        # performance
        self.dv                 = self.calc_total_dv()

        # flight recorder
        self.flight_recorder    = FlightRecorder()



    def calc_initial_velocity(self, lat):

        speed                   = Earth.surface_speed(self.position)
        x                       = self.position.x
        y                       = self.position.y

        velocity                = Vector3D([-y, x, 0]).unit()
        velocity.scale(speed)

        return velocity



    def sum_stage_masses(self):

        stage_masses            = sum([x.mass for x in self.stages])

        return stage_masses



    def calc_total_dv(self):

        dv = 0.0

        # iterate over stages
        for i, stage in enumerate(self.stages):

            dry_mass            = 0.0
            prop_mass           = 0.0

            # get mass of stage plus all stages above
            for j in range(Params.stages, -1, -1):

                if j-1 > i:

                    dry_mass += self.stages[j-1].mass

                elif j-1 == i:

                    dry_mass  += self.stages[j-1].dry_mass
                    prop_mass += self.stages[j-1].prop_mass

            init              = dry_mass + prop_mass
            final             = dry_mass

            dv                += calc_dv(init, final, stage.isp)

        return dv




    def get_current_state(self):

        state           = self.stages[-1].state.vector
        self.position.update([state[0].p, state[1].p, state[2].p])
        self.velocity.update([state[0].v, state[1].v, state[2].v])

        state_rel       = self.stages[-1].state_rel.vector
        self.position_rel.update([state_rel[0].p, state_rel[1].p, state_rel[2].p])
        self.velocity_rel.update([state_rel[0].v, state_rel[1].v, state_rel[2].v])

        self.altitude   = orbital.utilities.altitude_from_radius(self.position.magnitude(), body=orbital.earth)
        self.downrange  = self.init_position.angle(self.position_rel) * Earth.radius_equator




    def modify_payload(self, payload):

        self.payload            = payload
        self.stages[-1].payload = payload
        self.stages[-1].update_mass()
        self.mass               = self.sum_stage_masses()
        self.thrust_GTOW        = self.stages[0].thrust / (self.mass * g_earth)




    def get_specs(self, txt=False, log=False, xls=False):

        text = [
            'Houndstooth Rocket',
            '--',
            'Total Mass: %s %.2f kg '              % (tabs(5), self.mass),
            'Payload Mass: %s %.1f kg '            % (tabs(4), self.payload),
            'Total Propellant Mass: %.2f kg '      % (sum([x.prop_mass for x in self.stages])),
            '%s Mass: %s %.2f kg '                 % (self.params.engine.Propellant['fuel'].id, tabs(4), sum([x.tank.fuel_mass for x in self.stages])),
            '%s Mass: %s %.2f kg '                 % (self.params.engine.Propellant['oxidizer'].id, tabs(6), sum([x.tank.lox_mass for x in self.stages])),
            'Total Height: %s %.2f m '             % (tabs(4), self.height),
            'Diameter: %s %.2f m '                 % (tabs(6), self.diameter),
            'L/D Ratio: %s %.2f '                  % (tabs(6), self.height/self.diameter),
            'Stages: %s %i \n'                     % (tabs(7), len(self.stages))
        ]
        for x, stage in enumerate(self.stages):
            j = 'SL' if x == 0 else 'VAC'
            text += [
                'Stage %i'                         % (x+1),
                '--',
                'Mass: %s %.2f kg '                % (tabs(8), self.stages[x].mass),
                'Thrust: %s %.1f N '               % (tabs(7), self.stages[x].thrust),
                'T/W Ratio: %s %.2f '              % (tabs(6), self.stages[x].thrust / (sum([x.mass for x in self.stages[x:]]) * g_earth)),
                'Engines: %s %i '                  % (tabs(7), Params.engines[x]),
                'Isp: %s %i '                      % (tabs(9), Params.engine.Isp[j][Params.performance]),
                'Burn Duration: %s %.1f s'         % (tabs(4), self.stages[x].burn_duration),
                'Tank Height: %s %.2f m '          % (tabs(5), self.stages[x].tank.height),
                'Tank Mass: %s %.2f kg '           % (tabs(6), self.stages[x].tank.dry_mass),
                'Fuel Tank Height: %s %.2f m '     % (tabs(2), self.stages[x].tank.fuel_h),
                'Fuel Mass: %s %.2f kg '           % (tabs(6), self.stages[x].tank.fuel_mass),
                'Fuel Tank Volume: %s %.2f m**3'   % (tabs(2), self.stages[x].tank.fuel_vol),
                'LOx Tank Height: %s %.2f m '      % (tabs(3), self.stages[x].tank.lox_h + self.params.tank_caps * 2),
                'LOx Mass: %s %.2f kg '            % (tabs(6), self.stages[x].tank.lox_mass),
                'LOx Tank Volume: %s %.2f m**3'    % (tabs(3), self.stages[x].tank.lox_vol),
                'N2 Tank Mass: %s %.2f kg '        % (tabs(4), self.stages[x].nitrogen_tank.dry_mass),
                'N2 Mass: %s %.2f kg '             % (tabs(7), self.stages[x].nitrogen_tank.commodity_mass),
                'Helium Tank Mass: %s %.2f kg '    % (tabs(2), sum([h.dry_mass for h in self.stages[x].helium_tanks])),
                'Helium Mass: %s %.2f kg '         % (tabs(5), sum([h.commodity_mass for h in self.stages[x].helium_tanks])),
                '\n'
            ]


        if txt == True:

            with open("rocket.txt", "w") as file:

                for x in text:
                    file.write(x + '\n')


        if log == True:

            for x in text:
                print(x)


        if xls == True:

            import pyexcel

            data = [['diameter', self.diameter * 1000, 'mm'], ['fairingLength', self.fairing.length * 1000, 'mm']]
            data += [['engine_offset', Params.engine.offset, 'mm']]
            data += [['stage_offset', self.stages[1].tank.height + Params.engine.height + Params.engine.offset, 'mm']]

            for x, stage in enumerate(self.stages):
                data += [['fuelTank%i_height'   % (x+1), round(self.stages[x].tank.fuel_h * 1000, 0), 'mm']]
                data += [['loxTank%i_height'    % (x+1), round((self.stages[x].tank.lox_h + self.params.tank_caps * 2) * 1000, 0), 'mm']]
                data += [['tank%i_cylThickness' % (x+1), round(self.stages[x].tank.cyl_t * 1000, 2), 'mm']]
                data += [['tank%i_crThickness'  % (x+1), round(self.stages[x].tank.cr_t * 1000, 2), 'mm']]

            pyexcel.save_as(array=data, dest_file_name="inventor_params.xlsx")



# Recursive

def compute_max_payload(error=0.0, integral=0.0, payload=100.0):

    gain                = 0.2
    tau_i               = 0.001
    new_payload         = payload + (gain * error + tau_i * integral)
    print("Error: %.2f, Integral: %.2f, Payload: %.2f" % (error,integral,new_payload))
    params              = copy.deepcopy(Params)
    odyne               = Rocket(params)
    odyne.modify_payload(new_payload)
    odyne.trajectory.optimize_pitchover()
    odyne.trajectory.simulate()
    sim                 = odyne.trajectory.simulation
    stage               = odyne.trajectory.rocket.stages[-1]
    error               = stage.prop_mass - (sim.circ_fuel + sim.circ_lox + stage.fuel_resid + stage.lox_resid)
    print(error)
    integral            += error

    if error < 0.0:
        odyne.modify_payload(payload)
        return odyne
    else:
        return compute_max_payload(error, integral, new_payload)






if __name__ == '__main__':

    # odyne = compute_max_payload()

    odyne = Rocket(Params)
    odyne.modify_payload(100.0)
    # # # odyne.get_specs(txt=True)
    # odyne.trajectory.optimize_pitchover()
    odyne.trajectory.simulate()
    odyne.flight_recorder.save_kml()
    # odyne.flight_recorder.graph('Altitude')           # Altitude, Velocity, Drag, Acceleration, Propellant, Downrange
    # odyne.flight_recorder.graph('Velocity')           # Altitude, Velocity, Drag, Acceleration, Propellant, Downrange
    # odyne.flight_recorder.graph('Acceleration')           # Altitude, Velocity, Drag, Acceleration, Propellant, Downrange
    # odyne.flight_recorder.graph('Downrange')           # Altitude, Velocity, Drag, Acceleration, Propellant, Downrange
    # Render3D(odyne.flight_recorder.data).animate()
