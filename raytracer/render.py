"""The core ray tracing algorithm: intersection, Phong shading, shadows,
recursive reflections and jittered-sample anti-aliasing."""

import random

from .vec3 import Vec3

MAX_REFLECTION_DEPTH = 4
SHADOW_BIAS = 1e-4


def find_closest_hit(scene, origin, direction):
    """Return (t, object) for the nearest object the ray hits, or (None, None)."""
    closest_t = None
    closest_obj = None
    for obj in scene.objects:
        t = obj.intersect(origin, direction)
        if t is not None and (closest_t is None or t < closest_t):
            closest_t = t
            closest_obj = obj
    return closest_t, closest_obj


def is_in_shadow(scene, point, light):
    to_light = light.position - point
    distance = to_light.length()
    if distance == 0:
        return False
    direction = to_light.normalize()
    for obj in scene.objects:
        t = obj.intersect(point, direction)
        if t is not None and t < distance:
            return True
    return False


def shade(scene, point, normal, view_dir, material):
    """Phong local illumination: ambient + diffuse + specular, summed over lights."""
    color = material.color * material.ambient
    for light in scene.lights:
        shadow_origin = point + normal * SHADOW_BIAS
        if is_in_shadow(scene, shadow_origin, light):
            continue

        light_dir = (light.position - point).normalize()
        diffuse_term = max(normal.dot(light_dir), 0.0)
        if diffuse_term > 0:
            color = color + material.color.multiply(light.color) * (
                material.diffuse * diffuse_term * light.intensity
            )

            reflect_dir = (-light_dir).reflect(normal)
            spec_angle = max(reflect_dir.dot(view_dir), 0.0)
            if spec_angle > 0:
                spec_term = spec_angle ** material.shininess
                color = color + light.color * (material.specular * spec_term * light.intensity)
    return color


def trace_ray(scene, origin, direction, depth=0):
    t, obj = find_closest_hit(scene, origin, direction)
    if obj is None:
        return scene.background

    point = origin + direction * t
    normal = obj.normal_at(point)
    view_dir = -direction
    local_color = shade(scene, point, normal, view_dir, obj.material)

    reflectivity = obj.material.reflectivity
    if depth < MAX_REFLECTION_DEPTH and reflectivity > 0.0:
        reflect_dir = direction.reflect(normal).normalize()
        reflect_origin = point + normal * SHADOW_BIAS
        reflected_color = trace_ray(scene, reflect_origin, reflect_dir, depth + 1)
        local_color = local_color * (1.0 - reflectivity) + reflected_color * reflectivity

    return local_color


def render(scene, camera, width, height, samples_per_pixel=1, seed=None):
    """Render the scene to a flat bytearray of RGB bytes, row-major, top to bottom."""
    if seed is not None:
        random.seed(seed)

    pixels = bytearray(width * height * 3)
    for y in range(height):
        for x in range(width):
            color_sum = Vec3(0.0, 0.0, 0.0)
            for _ in range(samples_per_pixel):
                if samples_per_pixel > 1:
                    jitter_x = random.random() - 0.5
                    jitter_y = random.random() - 0.5
                else:
                    jitter_x = jitter_y = 0.0

                ndc_x = ((x + 0.5 + jitter_x) / width) * 2.0 - 1.0
                ndc_y = 1.0 - ((y + 0.5 + jitter_y) / height) * 2.0

                direction = camera.generate_ray(ndc_x, ndc_y)
                color_sum = color_sum + trace_ray(scene, camera.position, direction)

            averaged = color_sum * (1.0 / samples_per_pixel)
            r, g, b = averaged.to_bytes()
            idx = (y * width + x) * 3
            pixels[idx] = r
            pixels[idx + 1] = g
            pixels[idx + 2] = b
    return pixels
