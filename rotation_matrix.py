import math
from earth      import Earth
from vector3d   import Vector3D



def rotation_angle(t):

    return 2 * math.pi * (t / Earth.day)



def seconds(hours):

    return hours * 3600



def rotate_Z(theta, vector):

    x       = vector.x
    y       = vector.y
    z       = vector.z

    x_prime = x * math.cos(theta) - y * math.sin(theta)
    y_prime = x * math.sin(theta) + y * math.cos(theta)
    z_prime = z

    return Vector3D([x_prime, y_prime, z_prime])





if __name__ == "__main__":

    # print( math.degrees(rotation_angle(seconds(6))) )

    theta = rotation_angle(seconds(6)) # 90 deg

    pos = Vector3D([1, 0, 0])

    print( rotate_Z(theta, pos).points )


    theta = rotation_angle(seconds(1))

    pos = Vector3D([1, 0, 0])

    for i in range(6):
        pos = rotate_Z(theta, pos)

    print(pos.points)
