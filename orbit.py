from math       import pi, sqrt
from earth      import Earth
from constants  import G_const



class Orbit(object):

    def __init__(self, perigee, apogee):

         self.perigee               = perigee
         self.apogee                = apogee
         self.semi_major_axis       = self.calc_semi_major_axis(self.perigee, self.apogee)

         if apogee > perigee:
             self.velocity_perigee  = self.calc_velocity_elliptical(self.semi_major_axis, perigee)
             self.velocity_apogee   = self.calc_velocity_elliptical(self.semi_major_axis, apogee)
         else:
             self.velocity_perigee  = self.calc_velocity_circular(perigee)
             self.velocity_apogee   = self.calc_velocity_circular(apogee)



    def update(self, perigee):

        self.__init__(perigee, self.apogee)




    def calc_semi_major_axis(self, perigee, apogee):
        ''' Calculates the semi-major axis given an apogee and perigee. '''

        return 0.5 * (Earth.radius_equator * 2 + perigee + apogee)




    def calc_velocity_elliptical(self, sMajAxis, altitude):
        ''' Calculates the velocity at altitude in an elliptical orbit with a given semi-major axis. '''

        return sqrt( (G_const * Earth.mass) * (2.0 / (Earth.radius_equator + altitude) - 1/sMajAxis) )




    def calc_velocity_circular(self, altitude):
        ''' Calculates the circular orbital velocity at a given apogee. '''

        return sqrt( (G_const * Earth.mass) / (Earth.radius_equator + altitude) )






if __name__ == '__main__':

    orbit1  = Orbit(145000, 504000)
    orbit2  = Orbit(-81000, 504000)
    orbit3  = Orbit(504000, 504000)
    print(orbit1.velocity_perigee, orbit2.velocity_apogee)

    circ1   = orbit3.velocity_apogee - orbit1.velocity_apogee
    circ2   = orbit3.velocity_apogee - orbit2.velocity_apogee
    diff    = circ2 - circ1

    print("145km x 504km circ dv: %f, -81km x 504km circ dv: %f, difference: %f" % (circ1, circ2, diff))
