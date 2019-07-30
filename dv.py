import math
from constants import g_earth



def calc_dv(initial, final, isp):
    ''' Implements the rocket equation: dv = isp * g * ln(m0/mf).

        Arguments:
            initial: mass of rocket prior to burn [kg].
            final: mass of rocket after burn [kg].
            isp: specific impulse [s].

        Returns:
            change in velocity (dv) [m/s].
    '''

    return isp * g_earth * math.log(initial/final)


def calc_m0(final, dv, isp):
    ''' Implements the rocket equation: dv = isp * g * ln(m0/mf) rearranged
        to compute the initial mass given a final mass, a desired deltaV and
        a specific impulse.

        Arguments:
            final: mass of rocket after burn [kg].
            dv: change in velocity [m/s].
            isp: specific impulse [s].

        Returns:
            initial mass of rocket prior to burn [kg].
    '''

    return final * math.e ** (dv / (isp * g_earth))


def calc_mf(initial, dv, isp):
    ''' Implements the rocket equation: dv = isp * g * ln(m0/mf) rearranged
        to compute the final mass given an initial mass, a desired deltaV and
        a specific impulse.

        Arguments:
            initial: mass of rocket prior to burn [kg].
            dv: change in velocity [m/s].
            isp: specific impulse [s].

        Returns:
            final mass of rocket after burn [kg].
    '''

    return initial * math.e ** (-dv / (isp * g_earth))








if __name__ == "__main__":

    dv = calc_dv(200, 100, 300)
    print(dv)

    mf = calc_mf(200, dv, 300)
    print(mf)
