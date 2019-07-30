import pyproj
import math
from params import Params

# Example position data, should be somewhere in Germany
# x = -3048050.675875282
# y = -1597433.6721748416
# z = 5352153.8966453755

lat = math.radians(Params.latitude)
lon = math.radians(Params.longitude)
alt = Params.altitude
print(lat, lon, alt)

ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
# x, y, z = pyproj.transform(lla, ecef, lon, lat, alt)
x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=True)
print(x, y, z)

# lon, lat, alt = pyproj.transform(ecef, lla, x, y, z, radians=True)
# print(lat, lon, alt)
#
# x, y, z = pyproj.transform(lla, ecef, lon, lat, alt, radians=True)
# print(x, y, z)
