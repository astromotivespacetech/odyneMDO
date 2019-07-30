import math
from engine                 import Hadley
from commodities.helium     import Helium
from commodities.aluminum   import Aluminum
from commodities.n2         import N2
from constants              import g_earth, atm_1, R_univ, T_stp
from units                  import pascal2psi, psi2pascal, cubicm2liter, liter2cubicm
from structures             import sphere_wall_thickness, sphere_mass


def hydrostatic_pressure(p, rho, h):

    return p + rho * g_earth * h



# IDEAL GAS LAW
# PV = nRT


def ideal_gas(T, n, X):

    # P = n(RT/V)
    # V = n(RT/P)
    # pressure equals number of moles times universal gas constant times temperature divided by volume
    # volume equals number of moles times universal gas constant times temperature divided by pressure

    # if X is pressure, will return volume; if X is volume, will return pressure

    return R_univ * T / X * n





# define target inlet pressure
# compute the hydrostatic pressure
# given a pressure [Pascal], temperature [K] and volume [m**3], get moles of helium

def moles(T, P, V):

    return (P * V) / (R_univ * T)






def nitrogen_volume(n, p):          # number of engines, pressure of tank

    # total nitrogen mass
    engine                       = Hadley
    engines                      = n
    chill                        = engine.Chill[N2.id]
    start                        = engine.Start[N2.id]
    shutdown                     = engine.Shutdown[N2.id]

    burn_duration                = 200.0
    IPS_flow_rate                = engine.IPS_purge[N2.id]
    IPS_mass                     = IPS_flow_rate * burn_duration
    resid                        = 0.5

    mass                         = (chill + start + shutdown + IPS_mass) * engines / resid
    moles                        = mass * 1000 / N2.mol
    v                            = ideal_gas(T_stp, moles, psi2pascal(p))

    print("Engines: %i" % (engines))
    print("Chill: %.2f kg, Start: %.2f kg, Shutdown: %.2f kg, IPS purge: %.2f kg" % (chill, start, shutdown, IPS_mass))
    print("Mass: %.2f kg, Moles: %.2f moles" % (mass, moles))
    print("volume: %.2f L" % (cubicm2liter(v)))
    print("Density: %.4f g/L" % ( mass * 1000 / cubicm2liter(v) ))




def helium_pressure(stage=1, liters=[19.0, 19.0], tanks=1):

    tank_vol = [
        {
            'fuel' : 2.37,  # [m**3] — use rocket.txt to update value
            'lox'  : 3.66   # [m**3] — use rocket.txt to update value
        },
        {
            'fuel' : 0.34,  # [m**3] — use rocket.txt to update value
            'lox'  : 0.52   # [m**3] — use rocket.txt to update value
        }
    ]

    inlet_pressure  = [Hadley.min_fuel_psia, Hadley.min_lox_psia]
    m_fuel          = moles(T_stp, inlet_pressure[stage-1], tank_vol[stage-1]['fuel'])
    m_lox           = moles(T_stp, inlet_pressure[stage-1], tank_vol[stage-1]['lox'])
    m               = [m_fuel, m_lox]

    if tanks==1:

        l           = liters[tanks-1]    # [Liter]
        m_resid     = moles(T_stp, max(inlet_pressure),  liter2cubicm(l))
        m           = sum(m) + m_resid
        p           = ideal_gas(T_stp, m, liter2cubicm(l)) # [Pascal]

        print("Moles: %f, Mass: %f g" % (m, m*Helium.mol))
        print("Liters: %.2f, Pressure: %f" % (l, pascal2psi(p)))

    else:

        for i in range(tanks):

            l       = liters[i]
            m_resid = moles(T_stp, inlet_pressure[i],  liter2cubicm(l))
            p       = ideal_gas(T_stp, m[i] + m_resid, liter2cubicm(l))

            print("%s Tank" % (list(tank_vol[i].keys())[i]))
            print("Moles: %f, Mass: %f g" % (m[i]+m_resid, (m[i]+m_resid)*Helium.mol))
            print("Liters: %.2f, Pressure: %f" % (l, pascal2psi(p)))









if __name__ == '__main__':

    # f = Hadley.Propellant['fuel'].rho
    # o = Hadley.Propellant['oxidizer'].rho
    #
    # p_f = hydrostatic_pressure(atm_1, f, 2.68)
    # p_o = hydrostatic_pressure(atm_1, o, 7.02)
    #
    # print(pascal2psi(p_o))



    # one mole of helium at standard pressure, temperature
    # m = moles(T_stp, atm_1, 0.0224)
    # print("Moles: %f, Mass: %f g" % (m, m*Helium.mol))

    # m = moles(T_stp, Hadley.start_pressure, 1.0)
    # print("Moles: %f, Mass: %f g" % (m, m*Helium.mol))


    # m = moles(T_stp, psi2pascal(40.0), 6.53)
    # print("Moles: %f, Mass: %f g" % (m, m*Helium.mol))





    # Helium pressure

    stage       = 1
    # tank_vols   = [78.0, 0.0]    # CTD, Inc
    # tank_vols   = [33.8, 33.8]    # CTD, Inc
    # tank_vols   = [19.0, 19.0]    # https://steelheadcomposites.com/composite-pressure-vessels/
    tank_vols   = [10.0, 0.0]    # https://steelheadcomposites.com/composite-pressure-vessels/
    num_tanks   = 1

    helium_pressure(stage, tank_vols, num_tanks)    # [stage, tank volume(s), number of tanks]



    # Nitrogen Volume

    num_engines         = 2
    n2_tank_pressure    = 5000

    nitrogen_volume(num_engines, n2_tank_pressure)



    # end
