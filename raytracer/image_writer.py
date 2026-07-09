"""A minimal, dependency-free PNG encoder.

Only the standard library is used: ``zlib`` for DEFLATE compression of
the image data (as PNG requires) and ``struct``/``zlib.crc32`` for
chunk framing. No Pillow, no numpy.
"""

import struct
import zlib

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(tag, data):
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(path, width, height, rgb_bytes):
    """Write an 8-bit RGB image to ``path`` as a PNG file.

    ``rgb_bytes`` must be a flat, row-major buffer of length
    ``width * height * 3`` (as produced by ``render.render``).
    """
    expected_len = width * height * 3
    if len(rgb_bytes) != expected_len:
        raise ValueError(
            f"rgb_bytes has length {len(rgb_bytes)}, expected {expected_len} "
            f"for a {width}x{height} RGB image"
        )

    ihdr = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,  # bit depth
        2,  # color type: truecolor (RGB)
        0,  # compression method
        0,  # filter method
        0,  # interlace method
    )

    stride = width * 3
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0 ("None") for every scanline
        raw.extend(rgb_bytes[y * stride:(y + 1) * stride])

    idat = zlib.compress(bytes(raw), 9)

    with open(path, "wb") as f:
        f.write(PNG_SIGNATURE)
        f.write(_chunk(b"IHDR", ihdr))
        f.write(_chunk(b"IDAT", idat))
        f.write(_chunk(b"IEND", b""))
