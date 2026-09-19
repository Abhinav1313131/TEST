#!/usr/bin/env python3
"""Generate a 64x64 Minecraft Java Edition skin (classic/wide arms).

Every body part is authored as a small character grid, one character per
texel, so the art can be edited by hand without an image editor.
Run: python3 generate_skin.py [output.png]
"""

import struct
import sys
import zlib

SIZE = 64

PALETTE = {
    ".": (0, 0, 0, 0),        # transparent
    "s": (229, 177, 137, 255),  # skin
    "S": (240, 199, 164, 255),  # skin highlight
    "d": (196, 142, 104, 255),  # skin shadow
    "k": (23, 23, 28, 255),     # hair
    "K": (38, 38, 47, 255),     # hair sheen
    "b": (14, 14, 18, 255),     # brow
    "w": (243, 240, 234, 255),  # eye white
    "i": (58, 42, 30, 255),     # iris
    "m": (142, 84, 74, 255),    # mouth
    "u": (43, 48, 58, 255),     # suit
    "U": (54, 61, 73, 255),     # suit highlight (pockets)
    "v": (33, 37, 45, 255),     # suit shadow
    "c": (69, 77, 92, 255),     # collar / placket
    "n": (174, 180, 192, 255),  # button
    "p": (39, 44, 53, 255),     # trousers
    "o": (18, 19, 24, 255),     # shoe
}

# --- head -------------------------------------------------------------
HEAD_TOP = [
    "kkkkkkkk",
    "kkKKKKkk",
    "kKKKKKKk",
    "kKKkkKKk",
    "kKKkkKKk",
    "kKKKKKKk",
    "kkKKKKkk",
    "kkkkkkkk",
]
HEAD_BOTTOM = ["dddddddd"] * 8
HEAD_FRONT = [
    "kkkkkkkk",
    "kksssskk",
    "kbbssbbk",
    "kwissiwk",
    "sssddsss",
    "dssssssd",
    "sssmmsss",
    "dssssssd",
]
HEAD_RIGHT = [
    "kkkkkkkk",
    "kkkkkkkk",
    "kkkkkkkb",
    "kkkkkkss",
    "kkkkksss",
    "kkkdssss",
    "kkssssss",
    "kdssssss",
]
HEAD_LEFT = [row[::-1] for row in HEAD_RIGHT]
HEAD_BACK = [
    "kkkkkkkk",
    "kkkkkkkk",
    "kkkkkkkk",
    "kkkkkkkk",
    "kkkkkkkk",
    "kkkkkkkk",
    "kddddddk",
    "kddddddk",
]

# --- hair overlay (hat layer) gives the swept-back volume --------------
HAT_TOP = ["kkkkkkkk"] * 8
HAT_BOTTOM = ["........"] * 8
HAT_FRONT = ["kkkkkkkk", "kk....kk"] + ["........"] * 6
HAT_RIGHT = ["kkkkkkkk", "kkkkkkkk", "kkkkk..."] + ["........"] * 5
HAT_LEFT = [row[::-1] for row in HAT_RIGHT]
HAT_BACK = ["kkkkkkkk"] * 4 + ["........"] * 4

# --- torso: closed-collar (Mao/Zhongshan) suit ------------------------
BODY_FRONT = [
    "cccccccc",
    "uuucuuuu",
    "uuunuuuu",
    "uUUcuUUu",
    "uuucuuuu",
    "uuunuuuu",
    "uuucuuuu",
    "uUUcuUUu",
    "uUUnuUUu",
    "uuucuuuu",
    "uuucuuuu",
    "vvvvvvvv",
]
BODY_BACK = ["cccccccc"] + ["uuuuuuuu"] * 10 + ["vvvvvvvv"]
BODY_RIGHT = ["cccc"] + ["vuuu"] * 10 + ["vvvv"]
BODY_LEFT = ["cccc"] + ["uuuv"] * 10 + ["vvvv"]
BODY_TOP = ["cccccccc", "cccssccc", "cccssccc", "cccccccc"]
BODY_BOTTOM = ["vvvvvvvv"] * 4

# --- limbs ------------------------------------------------------------
SLEEVE = ["uuuu"] * 9 + ["cccc"] + ["ssss"] * 2
ARM_TOP = ["uuuu"] * 4
HAND = ["ssss"] * 4
TROUSER = ["pppp"] * 8 + ["vvvv"] + ["oooo"] * 3
LEG_TOP = ["pppp"] * 4
SOLE = ["oooo"] * 4


def blank():
    return [[PALETTE["."]] * SIZE for _ in range(SIZE)]


def paint(img, x, y, rows):
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            img[y + dy][x + dx] = PALETTE[ch]


def box(img, ox, oy, w, d, h, faces):
    """Paint one Minecraft box unwrap at (ox, oy) for a w x h x d part."""
    top, bottom, right, front, left, back = faces
    paint(img, ox + d, oy, top)
    paint(img, ox + d + w, oy, bottom)
    paint(img, ox, oy + d, right)
    paint(img, ox + d, oy + d, front)
    paint(img, ox + d + w, oy + d, left)
    paint(img, ox + d + w + d, oy + d, back)


def build():
    img = blank()
    head = (HEAD_TOP, HEAD_BOTTOM, HEAD_RIGHT, HEAD_FRONT, HEAD_LEFT, HEAD_BACK)
    hat = (HAT_TOP, HAT_BOTTOM, HAT_RIGHT, HAT_FRONT, HAT_LEFT, HAT_BACK)
    body = (BODY_TOP, BODY_BOTTOM, BODY_RIGHT, BODY_FRONT, BODY_LEFT, BODY_BACK)
    arm = (ARM_TOP, HAND, SLEEVE, SLEEVE, SLEEVE, SLEEVE)
    leg = (LEG_TOP, SOLE, TROUSER, TROUSER, TROUSER, TROUSER)

    box(img, 0, 0, 8, 8, 8, head)     # head
    box(img, 32, 0, 8, 8, 8, hat)     # hair overlay
    box(img, 16, 16, 8, 4, 12, body)  # torso
    box(img, 40, 16, 4, 4, 12, arm)   # right arm
    box(img, 32, 48, 4, 4, 12, arm)   # left arm
    box(img, 0, 16, 4, 4, 12, leg)    # right leg
    box(img, 16, 48, 4, 4, 12, leg)   # left leg
    return img


def write_png(path, img):
    raw = b"".join(
        b"\x00" + bytes(v for px in row for v in px) for row in img
    )

    def chunk(tag, data):
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "leader-suit-skin.png"
    write_png(out, build())
    print("wrote", out)
