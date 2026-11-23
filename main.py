#!/usr/bin/env python3
"""news-image-20261123 entrypoint.

Copies the pre-rendered poster entry.png (drawn by poster.py in this
session) into MAKEFUN_OUTPUT_DIR as entry.png. Standard library only,
deterministic: the same bytes out on every run.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    src = os.path.join(HERE, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    # the gate caps the image at 1 MiB and 1024x1024; refuse loudly if
    # the committed poster ever grows past the cap instead of entering
    # an invalid file.
    if os.path.getsize(dst) > 1048576:
        raise SystemExit("entry.png exceeds the 1 MiB gate cap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
