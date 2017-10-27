#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Life's pathetic, have fun ("▔□▔)/hi~♡ Nasy.

Excited without bugs::

    |             *         *
    |                  .                .
    |           .
    |     *                      ,
    |                   .
    |
    |                               *
    |          |\___/|
    |          )    -(             .              '
    |         =\  -  /=
    |           )===(       *
    |          /   - \
    |          |-    |
    |         /   -   \     0.|.0
    |  NASY___\__( (__/_____(\=/)__+1s____________
    |  ______|____) )______|______|______|______|_
    |  ___|______( (____|______|______|______|____
    |  ______|____\_|______|______|______|______|_
    |  ___|______|______|______|______|______|____
    |  ______|______|______|______|______|______|_
    |  ___|______|______|______|______|______|____

* author: Nasy
* date: Oct 15, 2017
* email: sy_n@me.com
* file: tools.py
* license: MIT

Copyright © 2017 by Nasy. All Rights Reserved.
"""
import os

from PIL import Image

from config import settings

SETTINGS = settings()


def pic_filter() -> None:
    """Filter pictures."""
    pics = os.listdir("pictures")

    def _filter(path: str) -> bool:
        """Filter."""
        pic = Image.open(f"pictures/{path}")
        width, height = pic.size
        if (width < SETTINGS["filter"]["min_width"] or
                height < SETTINGS["filter"]["min_height"] or
                width / height < SETTINGS["filter"]["min_w2h"] or
                width / height > SETTINGS["filter"]["max_w2h"]):
            return False
        return True

    left = map(_filter, pics)
    for l, p in zip(left, pics):
        if not l:
            os.rename(f"pictures/{p}", f"pictures/n{p}")


def main() -> None:
    """Yooo main function."""
    pic_filter()


if __name__ == "__main__":
    main()
