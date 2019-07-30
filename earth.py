import math
from vector3d   import Vector3D
from constants  import G_const



class Earth(object):

    radius_equator          = 6378137  # meters (at equator)
    f                       = 1/298.257223563
    radius_poles            = radius_equator * (1-f)  # 6356752.314245179 meters (at poles)
    omega                   = 7.2921159e-5 # angular velocity [radians/second]
    center                  = Vector3D([0,0,0])
    mass                    = 5.97237e+24 # [kg]
    e                       = math.sqrt((radius_equator**2-radius_poles**2)/radius_equator**2)
    e_prime                 = math.sqrt((radius_equator**2-radius_poles**2)/radius_poles**2)
    circumference           = 2 * math.pi * radius_equator
    day                     = 86164


    @classmethod
    def calc_gravity(cls, distance):
        ''' Given an altitude, returns force of gravity in m/s^2 '''

        return G_const * Earth.mass / distance ** 2




    @classmethod
    def get_cartesian(cls, lat, lon, alt):

        a       = Earth.radius_equator
        b       = Earth.radius_poles

        N       = a / math.sqrt(1 - Earth.e ** 2 * math.sin(math.radians(lat))**2)

        x       = (N + alt) * math.cos(math.radians(lat)) * math.cos(math.radians(lon))
        y       = (N + alt) * math.cos(math.radians(lat)) * math.sin(math.radians(lon))
        z       = ((b**2/a**2) * N + alt) * math.sin(math.radians(lat))

        v       = Vector3D([x, y, z])

        return v



    @classmethod
    def get_lat_lon(cls, vector):

        x       = vector.x
        y       = vector.y
        z       = vector.z

        a       = Earth.radius_equator
        b       = Earth.radius_poles
        p       = math.sqrt(x**2 + y**2)

        lon     = math.atan2(y,x)

        theta   = math.atan2((z*a),(p*b))

        num     = z + Earth.e_prime**2 * b * math.sin(theta)**3
        den     = p - Earth.e**2 * a * math.cos(theta)**3

        lat     = math.atan2(num,den)

        N       = a / math.sqrt(1 - Earth.e ** 2 * math.sin(lat)**2)

        h       = p / math.cos(lat) - N


        return lat, lon, h




    @classmethod
    def velocity_at_latitude(cls, lat):
        ''' Given a latitude in degrees, returns the tangential velocity at sea-level. '''

        return Earth.radius_equator * Earth.omega * math.cos(math.radians(lat))



    @classmethod
    def surface_speed(cls, vector):

        x               = vector.x
        y               = vector.y
        radius          = math.sqrt(x**2 + y**2)

        circumference   = 2 * math.pi * radius
        speed           = circumference / Earth.day

        return speed



    @classmethod
    def radius_at_latitude(cls, lat):

        r1       = Earth.radius_equator
        r2       = Earth.radius_poles
        n        = (r1**2 * math.cos(lat))**2 + (r2**2 * math.sin(lat))**2
        d        = (r1 * math.cos(lat))**2 + (r2 * math.sin(lat))**2
        r        = math.sqrt(n/d)

        return r




if __name__ == '__main__':

    # E = Earth()
    # v = E.get_cartesian(28, 0)

    # lat         = 57.43498194
    # lon         = -152.34169916
    # alt         = 30.0

    lat = 45
    lon = 0
    alt = 0

    c           = Earth.get_cartesian(lat, lon, alt)

    r = Earth.velocity_at_latitude(lat)
    s = Earth.surface_speed(c)
    print(r, s)
