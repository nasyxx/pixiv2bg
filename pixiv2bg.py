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
* date: Oct 12, 2017
* email: sy_n@me.com
* file: pixiv2bg.py
* license: MIT

Copyright © 2017 by Nasy. All Rights Reserved.
"""
import asyncio
import os
from typing import Any, Dict, Set

import aiohttp
import uvloop
from tqdm import tqdm

URL = "https://api.pixiv.moe/v1/ranking?page="


async def fetch_page(page: int = 1) -> Dict[str, Any]:
    """Fetch pixiv.moe page."""
    async with aiohttp.ClientSession() as session:
        async with session.get(URL + str(page)) as res:
            return await res.json()


async def fetch_illust(url: str, title: str):
    """Fetch illusts."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            try:
                os.mkdir("pictures")
            except FileExistsError:
                pass
            with open(f"pictures/{title}.{url[-4:].split('.')[1]}", "wb") as f:
                while True:
                    chunk = await res.content.read(5)
                    if not chunk:
                        break
                    f.write(chunk)


async def add_illust(illust: Dict[str, Any], stores: Set[str], t: Any):
    """Add illusts."""
    if "None" in stores or illust["unique_id"] not in stores:
        width, height, tags = (
            illust["work"]["width"], illust["work"]["height"],
            illust["work"]["tags"]
        )
        if width > 1440 or width > 1000 and width / height >= 1:
            if "漫画" not in tags:
                await fetch_illust(
                    illust["work"]["image_urls"]["large"],
                    illust["work"]["title"]
                )
                t.update()
                return illust["unique_id"]
    t.update()
    return "None"


def main() -> None:
    """Run this task."""
    config = {}  # type: Dict[str, str]
    stores = set()  # type: Set[str]
    add = stores.add
    with open("configs") as f:
        for line in f:
            key, value = line.replace(" ", "").replace("\n", "").split(":")
            config[key] = value
    if config.get("store", "true").lower() == "true":
        try:
            with open("store") as s:
                for i in s.read().split("\n"):
                    add(i)
        except FileNotFoundError:
            add("None")
    else:
        add("None")

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    fetch = asyncio.ensure_future(fetch_page())
    loop.run_until_complete(fetch)
    works = fetch.result()["response"]["works"]

    with tqdm(total = len(works)) as t:
        tasks = [
            asyncio.ensure_future(add_illust(work, stores, t))
            for work in works
        ]
        loop.run_until_complete(asyncio.wait(tasks))


if __name__ == "__main__":
    main()
