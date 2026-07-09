"""Minimal 3D vector class used for points, directions and RGB colors."""

import math


class Vec3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    __rmul__ = __mul__

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other):
        if not isinstance(other, Vec3):
            return NotImplemented
        return (
            math.isclose(self.x, other.x, abs_tol=1e-9)
            and math.isclose(self.y, other.y, abs_tol=1e-9)
            and math.isclose(self.z, other.z, abs_tol=1e-9)
        )

    def __repr__(self):
        return f"Vec3({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def multiply(self, other):
        """Component-wise product, used for tinting light color by surface color."""
        return Vec3(self.x * other.x, self.y * other.y, self.z * other.z)

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        length = self.length()
        if length == 0:
            return Vec3(0.0, 0.0, 0.0)
        inv = 1.0 / length
        return Vec3(self.x * inv, self.y * inv, self.z * inv)

    def reflect(self, normal):
        """Reflect this vector around a (unit-length) normal."""
        return self - normal * (2.0 * self.dot(normal))

    def clamp(self, lo=0.0, hi=1.0):
        return Vec3(
            min(max(self.x, lo), hi),
            min(max(self.y, lo), hi),
            min(max(self.z, lo), hi),
        )

    def to_bytes(self):
        """Convert a 0..1 color into three 0..255 integer bytes (gamma corrected)."""
        gamma = 1.0 / 2.2
        c = self.clamp(0.0, 1.0)
        r = int((c.x ** gamma) * 255 + 0.5)
        g = int((c.y ** gamma) * 255 + 0.5)
        b = int((c.z ** gamma) * 255 + 0.5)
        return min(r, 255), min(g, 255), min(b, 255)
