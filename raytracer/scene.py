"""Lights, camera and scene assembly, including the built-in demo scene."""

import math

from .vec3 import Vec3
from .shapes import Sphere, Plane, Material


class Light:
    def __init__(self, position, color=None, intensity=1.0):
        self.position = position
        self.color = color if color is not None else Vec3(1.0, 1.0, 1.0)
        self.intensity = intensity


class Camera:
    """A simple pinhole camera defined by position, look-at target and vertical FOV."""

    def __init__(self, position, look_at, up, fov_degrees, aspect_ratio):
        self.position = position
        self.aspect_ratio = aspect_ratio
        self.tan_half_fov = math.tan(math.radians(fov_degrees) / 2.0)

        forward = (look_at - position).normalize()
        right = forward.cross(up).normalize()
        true_up = right.cross(forward).normalize()

        self.forward = forward
        self.right = right
        self.up = true_up

    def generate_ray(self, ndc_x, ndc_y):
        """ndc_x, ndc_y are in [-1, 1] normalized device coordinates."""
        px = ndc_x * self.tan_half_fov * self.aspect_ratio
        py = ndc_y * self.tan_half_fov
        direction = (self.forward + self.right * px + self.up * py).normalize()
        return direction


class Scene:
    def __init__(self, objects, lights, background=None):
        self.objects = objects
        self.lights = lights
        self.background = background if background is not None else Vec3(0.05, 0.06, 0.09)


def demo_scene(aspect_ratio=4.0 / 3.0):
    """Build the sample scene rendered by ``main.py`` and used in tests.

    Three spheres of varying material (matte, glossy, mirror-like) resting
    on an infinite checker-free floor plane, lit by two point lights.
    """
    red_matte = Material(Vec3(0.8, 0.2, 0.2), reflectivity=0.0)
    blue_glossy = Material(Vec3(0.2, 0.3, 0.9), specular=1.0, shininess=400.0, reflectivity=0.25)
    mirror = Material(Vec3(0.9, 0.9, 0.9), diffuse=0.2, specular=1.0, shininess=800.0, reflectivity=0.75)
    floor_material = Material(Vec3(0.6, 0.6, 0.65), specular=0.1, reflectivity=0.05)

    objects = [
        Sphere(Vec3(-1.6, 0.0, -6.0), 1.0, red_matte),
        Sphere(Vec3(0.6, 0.6, -5.0), 1.4, blue_glossy),
        Sphere(Vec3(2.6, -0.3, -4.5), 0.8, mirror),
        Plane(Vec3(0.0, -1.4, 0.0), Vec3(0.0, 1.0, 0.0), floor_material),
    ]

    lights = [
        Light(Vec3(-5.0, 5.0, -2.0), Vec3(1.0, 1.0, 1.0), intensity=1.0),
        Light(Vec3(4.0, 3.0, -1.0), Vec3(0.6, 0.7, 1.0), intensity=0.6),
    ]

    scene = Scene(objects, lights)
    camera = Camera(
        position=Vec3(0.0, 0.7, 2.5),
        look_at=Vec3(0.0, 0.0, -5.0),
        up=Vec3(0.0, 1.0, 0.0),
        fov_degrees=60.0,
        aspect_ratio=aspect_ratio,
    )
    return scene, camera
