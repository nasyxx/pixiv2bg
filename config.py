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
* date: Oct 13, 2017
* update: Oct 15, 2017
* email: sy_n@me.com
* file: config.py
* license: MIT

Copyright © 2017 by Nasy. All Rights Reserved.
"""
from typing import Any, Dict


def settings() -> Dict[str, Any]:
    """Get settings."""
    return {
        "store": True,
        "file": "./store.json",
        "pages": 10,
        "filter": {
            "min_width": 1440,
            "min_height": 0,
            "min_w2h": 5 / 4,
            "max_w2h": 3 / 1,
            "tags": {"漫画"}
        }
    }
