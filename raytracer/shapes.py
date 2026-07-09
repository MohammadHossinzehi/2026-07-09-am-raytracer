"""Geometric primitives the ray tracer can intersect: spheres and planes."""

import math

from .vec3 import Vec3


class Material:
    """Surface appearance under the Phong reflection model."""

    def __init__(self, color, ambient=0.1, diffuse=0.9, specular=0.9,
                 shininess=200.0, reflectivity=0.0):
        self.color = color
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflectivity = reflectivity


class Sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.material = material

    def intersect(self, origin, direction):
        """Return the nearest positive t where the ray hits this sphere, or None."""
        oc = origin - self.center
        a = direction.dot(direction)
        b = 2.0 * oc.dot(direction)
        c = oc.dot(oc) - self.radius * self.radius
        discriminant = b * b - 4 * a * c
        if discriminant < 0:
            return None
        sqrt_disc = math.sqrt(discriminant)
        t1 = (-b - sqrt_disc) / (2 * a)
        t2 = (-b + sqrt_disc) / (2 * a)
        eps = 1e-4
        if t1 > eps:
            return t1
        if t2 > eps:
            return t2
        return None

    def normal_at(self, point):
        return (point - self.center).normalize()


class Plane:
    """An infinite plane defined by a point on it and a unit normal."""

    def __init__(self, point, normal, material):
        self.point = point
        self.normal = normal.normalize()
        self.material = material

    def intersect(self, origin, direction):
        denom = self.normal.dot(direction)
        if abs(denom) < 1e-6:
            return None
        t = (self.point - origin).dot(self.normal) / denom
        eps = 1e-4
        if t > eps:
            return t
        return None

    def normal_at(self, point):
        return self.normal
