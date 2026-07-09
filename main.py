#!/usr/bin/env python3
"""CLI entry point: render the built-in demo scene to a PNG file.

Example:
    python main.py --width 640 --height 480 --samples 4 --out render.png
"""

import argparse
import time

from raytracer.scene import demo_scene
from raytracer.render import render
from raytracer.image_writer import write_png


def main():
    parser = argparse.ArgumentParser(description="From-scratch Python ray tracer")
    parser.add_argument("--width", type=int, default=480, help="output image width in pixels")
    parser.add_argument("--height", type=int, default=360, help="output image height in pixels")
    parser.add_argument("--samples", type=int, default=4, help="samples per pixel (anti-aliasing)")
    parser.add_argument("--out", default="render.png", help="output PNG path")
    parser.add_argument("--seed", type=int, default=1, help="random seed for jittered sampling")
    args = parser.parse_args()

    scene, camera = demo_scene(aspect_ratio=args.width / args.height)

    start = time.time()
    pixels = render(scene, camera, args.width, args.height, args.samples, seed=args.seed)
    elapsed = time.time() - start

    write_png(args.out, args.width, args.height, pixels)
    print(
        f"Rendered {args.width}x{args.height} at {args.samples} sample(s)/pixel "
        f"in {elapsed:.2f}s -> {args.out}"
    )


if __name__ == "__main__":
    main()
