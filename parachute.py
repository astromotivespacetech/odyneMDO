import math
from constants          import g_earth
from atmosphere         import Atmosphere
from commodities.nylon  import Nylon





A = Atmosphere()


class Parachute(object):


    def __init__(self):

        self.C_d        = 1.75
        self.rho        = A.calc_rho(0.0)
        self.W          = 333.0 * g_earth               # [N]
        self.v          = 8.0                           # [m/s]
        self.material   = Nylon
        self.thickness  = 7.62e-5                       # [m] => 0.003 in

        self.S_A        = self.calc_surface_area()
        self.D          = self.calc_diameter()
        self.mass       = self.calc_mass()



    def calc_surface_area(self):

        return 2 * self.W / (self.rho * self.C_d * self.v ** 2)



    def calc_diameter(self):

        return 2 * math.sqrt(self.S_A / math.pi)



    def calc_mass(self):

        return self.S_A * self.thickness * self.material.density



    def attributes(self):

        print("Surface Area: %.2f sq. m\nDiameter: %.2f m\nMass: %.2f kg\n" % (self.S_A, self.D, self.mass) )




if __name__ == "__main__":

    chute = Parachute()
    chute.attributes()
