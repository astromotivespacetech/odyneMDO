from math import pi
from engine import Hadley
from commodities.kerosene import Kerosene


# F = πPr4 / 8nl

def flow_rate(P, r, n, l):

    return (pi * P * r**4) / (8 * n * l)



if __name__=="__main__":

    P = atm_1 * 0.1         # [pascal]
    r = 0.0127              # [m] (1 inch dia.)
    n = Kerosene.n
    l = 1                   # [m]

    # P =  atm_1 * 0.5 # [pascal]
    # r = 0.0005 # [m]
    # n = 0.001
    # l = 2 # [m]

    F = flow_rate(P,r,n,l)  # [m**3/s]
    m = F * Kerosene.rho    # [kg]

    print(m)
