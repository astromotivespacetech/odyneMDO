import math


class Vector3D(object):

    def __init__(self, points = [0.0, 0.0, 0.0]):
        self.points = points
        self.x      = self.points[0]
        self.y      = self.points[1]
        self.z      = self.points[2]


    def sum(self, vector):
        new = [x+y for x, y in zip(self.points, vector.points)]
        return Vector3D(new)


    def difference(self, vector):
        new = [x-y for x, y in zip(self.points, vector.points)]
        return Vector3D(new)


    def add(self, vector):
        for i, x in enumerate(vector.points):
            self.points[i] += x
        self.__init__(self.points)


    def subtract(self, vector):
        for i, x in enumerate(vector.points):
            self.points[i] -= x
        self.__init__(self.points)


    def scale(self, scalar):
        for x in range(len(self.points)):
            self.points[x] *= scalar
        self.__init__(self.points)


    def divide(self, scalar):
        for x in range(len(self.points)):
            self.points[x] /= scalar
        self.__init__(self.points)


    def dot(self, vector):
        new = sum([x*y for x, y in zip(self.points, vector.points)])
        return new


    def cross(self, vector):
        x = self.y * vector.z - self.z * vector.y
        y = self.z * vector.x - self.x * vector.z
        z = self.x * vector.y - self.y * vector.x
        return Vector3D([x,y,z])


    def copy(self):
        return Vector3D(list(self.points))


    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


    def unit(self):
        m = self.magnitude()
        if m == 0:
            new = [0, 0, 0]
        else:
            new = [1/m * self.x, 1/m * self.y, 1/m * self.z]
        return Vector3D(new)


    def inverse(self):
        new = [-1 * x for x in self.points]
        return Vector3D(new)


    def angle(self, vector):
        m1      = self.magnitude()
        m2      = vector.magnitude()
        dot     = self.dot(vector)

        if dot / (m1 * m2) > 1.0:
            n   = 1.0
        elif dot / (m1 * m2) < -1.0:
            n   = -1.0
        else:
            n   = dot / (m1 * m2)
        return math.acos(n)


    def update(self, array):
        self.__init__(array)
