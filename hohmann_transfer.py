from orbit import Orbit





def calc_hohmann_dv(init, final):
    ''' Computes the delta-v required to transfer from one circular orbit to
        another circular orbit in the same orbital plane. A new Orbit instance is
        created for the elliptical transfer orbit, using the apogees of the two
        circular orbits given. The required delta-v is the sum of the two burns
        that place the rocket in the elliptical transfer orbit, and the circularize
        the orbit.

        Args:
            init: can be either the initial circular altitude, or an Orbit instance
            final: can be either the final circular altitude, or an Orbit instance

        Returns:
            required change in velocity [m/s].
    '''


    init_orbit      = init  if isinstance(init, Orbit)  else Orbit(init, init)
    final_orbit     = final if isinstance(final, Orbit) else Orbit(final, final)
    transfer_orbit  = Orbit(min(init_orbit.apogee, final_orbit.apogee), max(init_orbit.apogee, final_orbit.apogee))

    if final_orbit.apogee > init_orbit.apogee:
        burn_1      = transfer_orbit.velocity_perigee - init_orbit.velocity_perigee
        burn_2      = final_orbit.velocity_apogee - transfer_orbit.velocity_apogee
    else:
        burn_1      = transfer_orbit.velocity_apogee - init_orbit.velocity_apogee
        burn_2      = final_orbit.velocity_perigee - transfer_orbit.velocity_perigee
    dv              = burn_1 + burn_2

    return abs(dv), burn_1, burn_2







if __name__ == "__main__":

    # orbit1 = Orbit(150000, 150000)
    # orbit2 = Orbit(500000, 500000)
    #
    # deltaV = calc_hohmann_dv(orbit2, orbit1)
    # print(deltaV)

    alt1   = 150000
    alt2   = 36000000   # geostationary altitude

    hohmann_transfer = calc_hohmann_dv(alt1, alt2)
    print(hohmann_transfer)
