''' Unit conversions.
'''

from __future__ import division


def meter2inch(x):
    return x / 0.0254

def inch2meter(x):
    return x * 0.0254

def psi2pascal(x):
    return x * 6895

def pascal2psi(x):
    return x / 6895

def lbf2newton(x):
    return x * 4.448

def newton2lbf(x):
    return x / 4.448

def lbm2kilogram(x):
    return x * 0.4536

def kilogram2lbm(x):
    return x / 0.4536

def ftlbf2newton(x):
    return x * 1.35582

def newton2ftlbf(x):
    return x * 0.73756

def u2kg(x):
    return x * 1.33

def kilo2unit(x):
    return x * 1000

def kelvin2celcius(x):
    return x - 273.15

def cubicm2liter(x):
    return x * 1000

def liter2cubicm(x):
    return x * 0.001
