import math

class Vector(object):
    x: int
    y: int

    @staticmethod
    def from_angle(angle: float, x_axis=False):
        if x_axis:
            return Vector(math.cos(angle), math.sin(angle))
        # Orthagonal left (y-axis)
        return Vector(-math.sin(angle), math.cos(angle))

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{{{0}, {1}}}".format(self.x, self.y)

    def add(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def sub(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def vector_projection(self, other):
        return self.scale(self.dot(other) / self.magsqr())

    def scalar_projection(self, other):
        return self.dot(other) / self.mag()
    
    def scale(self, factor: float):
        return Vector(self.x * factor, self.y * factor)

    def magsqr(self):
        return self.x * self.x + self.y * self.y

    def mag(self):
        return math.sqrt(self.magsqr())

    def to_tuple(self):
        return (self.x, self.y)

    def orthagonal(self, right):
        if right:
            return Vector(self.y, -self.x)
        return Vector(-self.y, self.x)

    def rotate(self, radians):
        sin = math.sin(radians)
        cos = math.cos(radians)
        return Vector(cos * self.x - sin * self.y, sin * self.x + cos * self.y)