from units                import *
from constants            import g_earth
from commodities.kerosene import Kerosene
from commodities.lox      import LOx


class Hadley(object):

    name                = 'Hadley'
    mass                = lbm2kilogram(60.9)        # [kg]
    height              = inch2meter(27.5)          # [m]
    offset              = 200                       # [mm]
    ox_f_ratio          = 2.17
    start_pressure      = psi2pascal(70.0)          # [psia]
    min_lox_psia        = psi2pascal(50.0)          # [psia]
    min_fuel_psia       = psi2pascal(40.0)          # [psia]


    thrust      = {
        'SL'            : lbf2newton(5000),
        'VAC'           : lbf2newton(5890)
    }

    Isp         = {
        'SL' : {
            'low'       : 258,
            'high'      : 270
        },
        'VAC' : {
            'low'       : 304,
            'high'      : 318
        }
    }

    flow_rate   = {
        'low'           : lbm2kilogram(19.375),
        'high'          : lbm2kilogram(18.522)
    }

    IPS_purge   = {
        'N2'           : lbm2kilogram(38.0) / 3600     # [kg/s] -- 38 lb/hr
    }

    Propellant  = {
        'fuel'          : Kerosene,
        'oxidizer'      : LOx
    }

    Chill       = {
        'Kerosene'      : lbm2kilogram(0),
        'LOx'           : lbm2kilogram(7),
        'N2'            : lbm2kilogram(0.55)
    }

    Start       = {
        'Kerosene'      : lbm2kilogram(6),
        'LOx'           : lbm2kilogram(13),
        'N2'            : lbm2kilogram(0.22)
    }

    Shutdown    = {
        'Kerosene'      : lbm2kilogram(6),
        'LOx'           : lbm2kilogram(20),
        'N2'            : lbm2kilogram(1.65)
    }






if __name__ == "__main__":

    sum_chill = sum([Hadley.Chill['Kerosene'],Hadley.Chill['LOx'],Hadley.Chill['N2']])
    sum_start = sum([Hadley.Start['Kerosene'],Hadley.Start['LOx'],Hadley.Start['N2']])
    sum_shutdown = sum([Hadley.Shutdown['Kerosene'],Hadley.Shutdown['LOx'],Hadley.Shutdown['N2']])

    print("Chill\n")
    print("Kerosene: %.2f" % Hadley.Chill['Kerosene'])
    print("LOx: %.2f" % Hadley.Chill['LOx'])
    print("N2: %.2f" % Hadley.Chill['N2'])
    print("Total: %.2f\n" % sum_chill)

    print("Start\n")
    print("Kerosene: %.2f" % Hadley.Start['Kerosene'])
    print("LOx: %.2f" % Hadley.Start['LOx'])
    print("N2: %.2f" % Hadley.Start['N2'])
    print("Total: %.2f\n" % sum_start)

    print("Shutdown\n")
    print("Kerosene: %.2f" % Hadley.Shutdown['Kerosene'])
    print("LOx: %.2f" % Hadley.Shutdown['LOx'])
    print("N2: %.2f" % Hadley.Shutdown['N2'])
    print("Total: %.2f\n" % sum_shutdown)

    print("Total Engine: %.2f" % sum([sum_chill + sum_start + sum_shutdown]))
