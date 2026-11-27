# main.py — entrypoint for the news-image-20261126 entry.
#
# Renders the same poster as poster.py and writes it, deterministically,
# to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png by default).
# Pure Python 3 standard library; no network, no installed fonts.
# Works under `python3 -P -s` from any working directory: the import
# of the sibling poster module is resolved via this file's own path.

import os
import sys

# The grader runs `python3 -P -s main.py`, and -P keeps the script's
# own directory off sys.path, so a plain `from poster import ...`
# fails with ModuleNotFoundError. Put this file's directory first on
# the path so the sibling module is found from any working directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from poster import render_poster


def main():
    # The grader runs this program twice; both runs must write the
    # same bytes, so render_poster() takes no input but the code.
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = render_poster()
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(data)


if __name__ == "__main__":
    main()
