

class R_4D(object):

    '''
        R-4D hypergolic bipropellant thruster by Aerojet Rocketdyne

        Sources:
        https://www.rocket.com/space/space-power-propulsion/bipropellant-space-propulsion
        http://www.astronautix.com/r/r-4d.html
    '''

    name        = 'R-4D'
    mass        = 5.44      # [kg]
    thrust      = 445       # [N]
    Isp         = 329       # [s]
    flow_rate   = {
        'fuel' : 0.05,      # [kg/sec]
        'ox'   : 0.091      # [kg/sec]
    }
    ox_f_ratio = 1.65
