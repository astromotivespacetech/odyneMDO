import math
from units      import *
from functions  import normalize
from vector3d   import Vector3D
from constants  import G_const
from earth      import Earth



class Atmosphere(object):


    def calc_rho(self, alt):
        ''' Calculates atmospheric density.

            Arguments:
                alt: altitude [km].

            Returns:
                atmospheric density [kg/m^3].
         '''

        a             = alt / 1000                                              # convert to [ km ]
        geopot_height = self.get_geopotential(a)                                # [ km ]
        temp          = self.get_standard_temperature(geopot_height)            # [ Kelvin ]
        standard_p    = self.get_standard_pressure(geopot_height, temp)         # [ Pascals ]
        R             = 287.5                                                   # specific gas constant for dry air

        return standard_p / (R * temp) if standard_p > 0 else 0.0


    def calc_ambient_pressure(self, alt):
        ''' Setup function for get_standard_pressure.

            Arguments:
                altitude [km]

            Returns:
                atmospheric pressure [Pascals].
        '''

        a             = alt / 1000                                              # convert to [ km ]
        geopot_height = self.get_geopotential(a)                                # [ km ]
        temp          = self.get_standard_temperature(geopot_height)            # [ Kelvin ]
        standard_p    = self.get_standard_pressure(geopot_height, temp)         # [ Pascals ]

        return standard_p if standard_p > 0 else 0.0



    def get_standard_pressure(self, g, t):                                      # returns atmospheric pressure in Pascals
        ''' Calculates standard atmosphere pressure up to 84.85 km.

            Arguments:
                g: geopotential height [km].
                t: temperature [Kelvin].

            Returns:
                pressure [Pascals].
        '''


        if g <= 11:
            return 101325   * math.pow(288.15 / t, -5.255877)
        elif g <= 20:
            return 22632.06 * math.exp(-0.1577 * (g - 11))
        elif g <= 32:
            return 5474.889 * math.pow(216.65 / t, 34.16319)
        elif g <= 47:
            return 868.0187 * math.pow(228.65 / t, 12.2011)
        elif g <= 51:
            return 110.9063 * math.exp(-0.1262 * (g - 47))
        elif g <= 71:
            return 66.93887 * math.pow(270.65 / t, -12.2011)
        elif g <= 84.85:
            return 3.956420 * math.pow(214.65 / t, -17.0816)
        else:
            return 0



    def get_standard_temperature(self, g):
        ''' Calculates standard temperature.

            Arguments:
                g: geopotential [km].

            Returns:
                temperature [Kelvin].
        '''

        if   g <= 11:
            return 288.15 - (6.5 * g)
        elif g <= 20:
            return 216.65
        elif g <= 32:
            return 196.65 + g
        elif g <= 47:
            return 228.65 + 2.8 * (g - 32)
        elif g <= 51:
            return 270.65
        elif g <= 71:
            return 270.65 - 2.8 * (g - 51)
        elif g <= 84.85:
            return 214.65 - 2 * (g - 71)
        else:
            return 0



    def get_geopotential(self, altitude_km):
        ''' Calculates geopotential height.

            Arguments:
                altitude_km: altitude [km].

            Returns:
                geopotential height [km].
        '''

        EARTH_RAD = Earth.radius_poles / 1000

        return EARTH_RAD * altitude_km / (EARTH_RAD + altitude_km)




    def speed_of_sound(self, alt):
        ''' Calculates the speed of sound at a given altitude.

            Arguments:
                alt: altitude [m].

            Returns:
                speed [m/s].
        '''

        a_km          = alt / 1000
        geopot_height = self.get_geopotential(a_km)
        temperature_k = self.get_standard_temperature(geopot_height)
        C             = kelvin2celcius(temperature_k)

        return 331.5 + 0.60 * C



    def calc_drag_coefficient(self, cd, a, s):
        ''' Approximates a mach-number-adjusted drag coefficient.
            Reference: https://history.nasa.gov/SP-367/f86.htm

            Arguments:
                cd: Drag Coefficient [unitless].
                a: altitude [m].
                s: speed [m/s].

            Returns:
                adjusted drag coefficient [unitless].

        '''

        mach_1      = self.speed_of_sound(a)
        mach_num    = normalize(s, 0, mach_1)

        max         = cd * 2

        if 0.8 <= mach_num < 1.0:
            drag_coef = cd + max * ((mach_num - 0.8) * 5)
        elif 1.0 <= mach_num < 3.0:
            drag_coef = cd + max * ((3.0 - mach_num) * 0.5)
        else:
            drag_coef = cd

        return drag_coef




    def calc_drag(self, component):
        ''' Returns aerodynamic drag force in Newtons.

            Arguments:
                rocket [object].
                stage [object] (optional).

            Returns:
                drag force [Newtons].
         '''

        # drag_coef = self.calc_drag_coefficient(rocket.C_d, rocket.altitude, rocket.velocity_rel.magnitude())
        #
        # if component:
        #     rho = self.calc_rho(component.a)
        #     return component.C_d * (rho * component.v.magnitude()**2 * 0.5) * component.x_A
        # else:
        #     rho = self.calc_rho(rocket.altitude)
        #     return drag_coef * (rho * rocket.velocity_rel.magnitude()**2 * 0.5) * rocket.x_A

        try:
            altitude = component.altitude
        except:
            altitude = Earth.get_lat_lon(component.position)[2]

        drag_coef = self.calc_drag_coefficient(component.C_d, altitude, component.velocity_rel.magnitude())

        rho = self.calc_rho(altitude)

        if component.C_d == 0.1:
            print(altitude, rho)

        return component.C_d * (rho * component.velocity_rel.magnitude()**2 * 0.5) * component.x_A


if __name__ == "__main__":

    a = Atmosphere()

    for x in range(100):

        c = a.calc_drag_coefficient(0.2, 10000, x*10)

        print(c)


# end
