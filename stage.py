import math
import copy
from constants      import T_stp
from functions      import normalize
from engine         import Hadley
from tanks          import PropellantTank
from runge_kutta    import StateVector
from pressure       import moles


class Stage(object):

    def __init__(self, stage, rocket):

        self.stage                  = stage
        self.params                 = rocket.params
        self.throttle               = self.params.throttle[stage]
        self.state                  = StateVector(rocket.position, rocket.velocity)
        self.state_rel              = StateVector(rocket.position_rel, rocket.velocity_rel)

        self.mass_ratio             = self.params.mass_ratios[stage]
        self.engines                = [self.params.engine() for _ in range(self.params.engines[stage])]

        self.nitrogen_tank          = self.params.nitrogen_tank(rocket, self)
        self.helium_tanks           = [self.params.helium_tank(stage) for _ in range(self.params.tanks_per_stage[stage])]

        if stage < self.params.stages - 1:
            self.interstage_mass    = self.params.interstage.mass
            self.payload            = 0
            self.fairing_mass       = rocket.fairing.mass                                                                                   if stage == 0 else 0
            self.fairing_length     = rocket.fairing.length                                                                                 if stage == 0 else 0
            self.recovery_mass      = self.params.recovery['ballute'] + self.params.recovery['parachute'] + self.params.recovery['drogues'] if stage == 0 else 0

        else:
            self.interstage_mass    = 0
            self.fairing_mass       = 0
            self.fairing_length     = 0
            self.recovery_mass      = 0
            self.payload            = rocket.payload

        # mass that is the same for each core
        self.core                   = sum([e.mass for e in self.engines]) + sum([h.mass for h in self.helium_tanks]) + self.nitrogen_tank.mass + self.recovery_mass

        # begin with inital mass
        self.init_dry_mass          = self.core + self.interstage_mass + self.fairing_mass + self.payload

        # compute dry mass, prop mass and tank
        self.dry_mass, self.prop_mass, self.tank = self.calc_mass_ratio(self.init_dry_mass)

        # add tank mass to core
        self.update_core_mass()

        # account for number of cores
        self.dry_mass               += (self.core * (self.params.cores[stage]-1))
        self.prop_mass              *= self.params.cores[stage]
        self.tanks                  = [copy.deepcopy(self.tank) for _ in range(self.params.cores[stage])]

        self.update_mass()
        self.height                 = self.tank.height + self.params.engine.height + self.fairing_length

        # extra params
        lox_moles                   = moles(T_stp, self.params.tank_pressure, self.tank.lox_vol) * self.params.helium_tank.commodity.mol
        fuel_moles                  = moles(T_stp, self.params.tank_pressure, self.tank.fuel_vol) * self.params.helium_tank.commodity.mol

        type                        = 'SL' if stage == 0 else 'VAC'
        self.thrust                 = self.params.engine.thrust[type] * len(self.engines) * self.params.cores[stage]
        self.isp                    = self.params.engine.Isp[type][self.params.performance]

        self.burn_duration          = self.calc_burn_duration()
        self.x_A                    = math.pi * (0.5 * rocket.diameter) ** 2
        self.C_d                    = 0.5
        self.recovery_status        = 1


    def calc_mass_ratio(self, dry_mass):

        prop_mass                   = self.mass_ratio * dry_mass - dry_mass
        tank                        = PropellantTank(prop_mass, self.params)
        dry_mass                    = self.init_dry_mass + tank.dry_mass
        mass_ratio                  = (prop_mass + dry_mass) / dry_mass

        if abs(mass_ratio - self.mass_ratio) < 0.001 * self.mass_ratio:
            return dry_mass, prop_mass, tank
        else:
            return self.calc_mass_ratio(dry_mass)



    def update_core_mass(self):

        self.core                   = sum([e.mass for e in self.engines]) + sum([h.mass for h in self.helium_tanks]) + self.nitrogen_tank.mass + self.tank.dry_mass + self.recovery_mass



    def update_prop_mass(self):

        self.prop_mass              = sum([tank.fuel_mass + tank.lox_mass for tank in self.tanks])


    def update_dry_mass(self):

        self.update_core_mass()
        self.dry_mass               = (self.core * self.params.cores[self.stage]) + self.interstage_mass + self.fairing_mass + self.payload



    def update_mass(self):

        self.update_dry_mass()
        self.update_prop_mass()
        self.mass                   = self.dry_mass + self.prop_mass



    def calc_burn_duration(self):

        flow_rate                   = self.params.engine.flow_rate[self.params.performance] * len(self.engines) * self.throttle

        return self.prop_mass / flow_rate
