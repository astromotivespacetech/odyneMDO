from geometries import *
from structures import crown_thickness, knuckle_thickness, cylinder_thickness
from engine     import Hadley



class PropellantTank(object):

    def __init__(self, prop_mass, params):

        self.params                     = params
        self.radius                     = params.diameter / 2.
        self.material                   = params.material
        self.prop_mass                  = prop_mass
        self.lox_mass, self.fuel_mass   = self.calc_fuel_lox_mass()
        self.lox_mass_residual          = self.lox_mass  / params.expulsion_efficiency - self.lox_mass
        self.fuel_mass_residual         = self.fuel_mass / params.expulsion_efficiency - self.fuel_mass
        self.lox_vol, self.fuel_vol     = self.calc_fuel_lox_vol()
        self.lox_h, self.fuel_h         = self.calc_tank_height()
        self.dry_mass                   = self.calc_tank_mass() * params.tank_piping
        self.height                     = self.lox_h + self.fuel_h + params.tank_caps * 2



    def calc_fuel_lox_mass(self):

        # calculate mass of non-propulsive fuel + oxidizer
        non_prop_fuel                   = Hadley.Chill['Kerosene'] + Hadley.Start['Kerosene'] + Hadley.Shutdown['Kerosene']
        non_prop_lox                    = Hadley.Chill['LOx']      + Hadley.Start['LOx']      + Hadley.Shutdown['LOx']
        prop_mass                       = self.prop_mass - non_prop_fuel - non_prop_lox

        # calculate propulsive fuel + oxidizer mass
        fuel_mass                       = prop_mass / (1 + Hadley.ox_f_ratio)
        lox_mass                        = prop_mass - fuel_mass

        # add non_prop mass back in
        fuel_mass                       += non_prop_fuel
        lox_mass                        += non_prop_lox

        return (lox_mass, fuel_mass)



    def calc_fuel_lox_vol(self):

        lox_vol         = self.lox_mass  / Hadley.Propellant['oxidizer'].rho / self.params.ullage['fuel']
        fuel_vol        = self.fuel_mass / Hadley.Propellant['fuel'].rho     / self.params.ullage['oxidizer']

        return (lox_vol, fuel_vol)



    def calc_tank_height(self):

        caps_vol        = ellipsoidal_vol(self.params.tank_caps,    self.radius)
        lox_cyl_height  = cylinder_height(self.lox_vol - caps_vol,  self.radius)
        fuel_cyl_height = cylinder_height(self.fuel_vol,            self.radius)

        return (lox_cyl_height, fuel_cyl_height)



    def calc_tank_mass(self):

        weld_eff        = 0.9
        stress          = self.material.max_stress
        rho             = self.material.rho
        pressure        = Hadley.start_pressure

        # get wall thicknesses
        cr_t            = crown_thickness(pressure, self.radius, stress, weld_eff)
        k_t             = knuckle_thickness(pressure, self.radius, self.params.tank_caps, stress, weld_eff)
        cyl_t           = cylinder_thickness(pressure, self.radius, stress, weld_eff)
        self.cr_t       = cr_t
        self.cyl_t      = cyl_t

        lox_cyl_mass    = cylinder_shell_mass(self.lox_h, self.radius, cyl_t, rho)
        lox_cap_mass    = ellipsoidal_shell_mass(self.params.tank_caps, self.radius, cr_t, rho)
        fuel_cyl_mass   = cylinder_shell_mass(self.fuel_h, self.radius, cyl_t, rho)
        fuel_cap_mass   = lox_cap_mass * 0.5

        return lox_cyl_mass + lox_cap_mass + fuel_cyl_mass + fuel_cap_mass
