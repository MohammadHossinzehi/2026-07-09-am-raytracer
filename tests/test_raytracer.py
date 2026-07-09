"""Unit tests for the vector math, geometry, and rendering pipeline."""

import math
import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from raytracer.vec3 import Vec3
from raytracer.shapes import Sphere, Plane, Material
from raytracer.scene import Camera, Light, Scene, demo_scene
from raytracer.render import find_closest_hit, is_in_shadow, trace_ray, render
from raytracer.image_writer import write_png


class TestVec3(unittest.TestCase):
    def test_add_and_sub(self):
        a = Vec3(1, 2, 3)
        b = Vec3(4, 5, 6)
        self.assertEqual(a + b, Vec3(5, 7, 9))
        self.assertEqual(b - a, Vec3(3, 3, 3))

    def test_scalar_mul(self):
        a = Vec3(1, -2, 3)
        self.assertEqual(a * 2, Vec3(2, -4, 6))
        self.assertEqual(2 * a, Vec3(2, -4, 6))

    def test_dot_and_cross(self):
        x = Vec3(1, 0, 0)
        y = Vec3(0, 1, 0)
        self.assertEqual(x.dot(y), 0.0)
        self.assertEqual(x.cross(y), Vec3(0, 0, 1))

    def test_length_and_normalize(self):
        v = Vec3(3, 4, 0)
        self.assertAlmostEqual(v.length(), 5.0)
        n = v.normalize()
        self.assertAlmostEqual(n.length(), 1.0)

    def test_normalize_zero_vector(self):
        self.assertEqual(Vec3(0, 0, 0).normalize(), Vec3(0, 0, 0))

    def test_reflect(self):
        incoming = Vec3(1, -1, 0).normalize()
        normal = Vec3(0, 1, 0)
        reflected = incoming.reflect(normal)
        self.assertAlmostEqual(reflected.x, incoming.x, places=5)
        self.assertAlmostEqual(reflected.y, -incoming.y, places=5)

    def test_to_bytes_clamps(self):
        r, g, b = Vec3(2.0, -1.0, 0.5).to_bytes()
        self.assertEqual(r, 255)
        self.assertEqual(g, 0)
        self.assertTrue(0 <= b <= 255)


class TestShapes(unittest.TestCase):
    def setUp(self):
        self.material = Material(Vec3(1, 0, 0))

    def test_sphere_hit(self):
        sphere = Sphere(Vec3(0, 0, -5), 1.0, self.material)
        t = sphere.intersect(Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertIsNotNone(t)
        self.assertAlmostEqual(t, 4.0, places=4)

    def test_sphere_miss(self):
        sphere = Sphere(Vec3(5, 5, -5), 1.0, self.material)
        t = sphere.intersect(Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertIsNone(t)

    def test_sphere_normal(self):
        sphere = Sphere(Vec3(0, 0, 0), 2.0, self.material)
        normal = sphere.normal_at(Vec3(2, 0, 0))
        self.assertEqual(normal, Vec3(1, 0, 0))

    def test_sphere_behind_ray_is_ignored(self):
        sphere = Sphere(Vec3(0, 0, 5), 1.0, self.material)
        t = sphere.intersect(Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertIsNone(t)

    def test_plane_hit(self):
        plane = Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), self.material)
        t = plane.intersect(Vec3(0, 5, 0), Vec3(0, -1, 0))
        self.assertAlmostEqual(t, 6.0, places=4)

    def test_plane_parallel_ray_misses(self):
        plane = Plane(Vec3(0, -1, 0), Vec3(0, 1, 0), self.material)
        t = plane.intersect(Vec3(0, 5, 0), Vec3(1, 0, 0))
        self.assertIsNone(t)


class TestCameraAndScene(unittest.TestCase):
    def test_camera_center_ray_points_at_target(self):
        camera = Camera(
            position=Vec3(0, 0, 0),
            look_at=Vec3(0, 0, -10),
            up=Vec3(0, 1, 0),
            fov_degrees=90,
            aspect_ratio=1.0,
        )
        direction = camera.generate_ray(0.0, 0.0)
        self.assertAlmostEqual(direction.x, 0.0, places=5)
        self.assertAlmostEqual(direction.y, 0.0, places=5)
        self.assertLess(direction.z, 0)

    def test_demo_scene_builds(self):
        scene, camera = demo_scene()
        self.assertGreater(len(scene.objects), 0)
        self.assertGreater(len(scene.lights), 0)
        self.assertIsInstance(camera, Camera)


class TestRenderPipeline(unittest.TestCase):
    def test_ray_with_no_hits_returns_background(self):
        scene = Scene(objects=[], lights=[], background=Vec3(0.1, 0.2, 0.3))
        color = trace_ray(scene, Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertEqual(color, Vec3(0.1, 0.2, 0.3))

    def test_find_closest_hit_picks_nearer_sphere(self):
        material = Material(Vec3(1, 1, 1))
        near = Sphere(Vec3(0, 0, -3), 1.0, material)
        far = Sphere(Vec3(0, 0, -8), 1.0, material)
        scene = Scene(objects=[far, near], lights=[])
        t, obj = find_closest_hit(scene, Vec3(0, 0, 0), Vec3(0, 0, -1))
        self.assertIs(obj, near)
        self.assertAlmostEqual(t, 2.0, places=4)

    def test_point_directly_under_light_is_not_in_shadow(self):
        scene = Scene(objects=[], lights=[])
        light = Light(Vec3(0, 5, 0))
        self.assertFalse(is_in_shadow(scene, Vec3(0, 0, 0), light))

    def test_occluded_point_is_in_shadow(self):
        material = Material(Vec3(1, 1, 1))
        blocker = Sphere(Vec3(0, 2.5, 0), 1.0, material)
        scene = Scene(objects=[blocker], lights=[])
        light = Light(Vec3(0, 5, 0))
        self.assertTrue(is_in_shadow(scene, Vec3(0, 0, 0), light))

    def test_render_produces_correctly_sized_buffer(self):
        scene, camera = demo_scene(aspect_ratio=1.0)
        pixels = render(scene, camera, width=6, height=4, samples_per_pixel=1)
        self.assertEqual(len(pixels), 6 * 4 * 3)

    def test_render_hits_are_not_all_background(self):
        # A ray through the center of the frame should hit the blue sphere
        # placed at the scene's focal point, not just the background.
        scene, camera = demo_scene(aspect_ratio=1.0)
        pixels = render(scene, camera, width=1, height=1, samples_per_pixel=1)
        bg_r, bg_g, bg_b = scene.background.to_bytes()
        self.assertFalse((pixels[0], pixels[1], pixels[2]) == (bg_r, bg_g, bg_b))


class TestImageWriter(unittest.TestCase):
    def test_write_png_roundtrip_signature(self):
        path = "/tmp/_raytracer_test_output.png"
        pixels = bytearray([255, 0, 0] * (2 * 2))
        write_png(path, 2, 2, pixels)
        with open(path, "rb") as f:
            data = f.read()
        self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertIn(b"IHDR", data)
        self.assertIn(b"IDAT", data)
        self.assertIn(b"IEND", data)
        os.remove(path)

    def test_write_png_rejects_wrong_buffer_size(self):
        with self.assertRaises(ValueError):
            write_png("/tmp/_should_not_be_created.png", 2, 2, bytearray([0, 0, 0]))


if __name__ == "__main__":
    unittest.main()
