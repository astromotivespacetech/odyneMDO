import math
from structures import ellipse_design_factor


def sphere_vol(r):
    return 4. / 3. * math.pi * r ** 3


def cylinder_vol(h, r):
    return h * math.pi * r ** 2


def ellipsoidal_vol(h, r):
    return 4. / 3. * math.pi * h * r ** 2


def sphere_shell_mass(r, t, a):
    return 4. / 3. * math.pi * r ** 2 * t * a


def cylinder_shell_mass(h, r, t, a):
    return 2 * math.pi * h * r * t * a


def ellipsoidal_shell_mass(h, r, t, a):
    k = r / h
    return math.pi * r**2 * t * a * ellipse_design_factor(k) / k


def cylinder_height(v, r):
    return v / (math.pi * r ** 2)
