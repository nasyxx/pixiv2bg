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
from typing import Any, Dict, Generator, Set

import aiohttp
import uvloop
from tqdm import tqdm

from config import settings

URL = "https://api.pixiv.moe/v1/ranking?page="
SETTINGS = settings()


async def illusts_filter(illusts: Dict[str, Any]) -> bool:
    """Filter the illusts."""
    work = illusts["work"]
    width, height, tags = work["width"], work["height"], work["tags"]
    for tag in tags:
        if tag in SETTINGS["filter"]["tags"]:
            return False
    if (width < SETTINGS["filter"]["min_width"] or
            height < SETTINGS["filter"]["min_height"] or
            width / height < SETTINGS["filter"]["min_w2h"] or
            width / height > SETTINGS["filter"]["max_w2h"]):
        return False
    return True


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
            with open((f"pictures/{title.replace('/','-')}."
                       f"{url[-4:].split('.')[-1]}"), "wb") as f:
                while True:
                    chunk = await res.content.read(5)
                    if not chunk:
                        break
                    f.write(chunk)


async def add_illust(illust: Dict[str, Any], stores: Set[int], t: Any):
    """Add illusts."""
    if ((0 in stores or illust["work"]["id"] not in stores) and
            await illusts_filter(illust)):
        await fetch_illust(
            illust["work"]["image_urls"]["large"], illust["work"]["title"]
        )
        t.update()
        return illust["work"]["id"]
    t.update()
    return 0


def main() -> None:
    """Run this task."""
    stores = set()  # type: Set[int]
    add = stores.add
    if SETTINGS.get("store", True):
        try:
            with open(SETTINGS["file"]) as s:
                for i in s.read().split("\n")[:-1]:
                    add(int(i))
        except FileNotFoundError:
            add(0)
    else:
        add(0)

    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)

    fetchs = [
        asyncio.ensure_future(fetch_page(p + 1))
        for p in range(int(SETTINGS["pages"]))
    ]

    loop.run_until_complete(asyncio.wait(fetchs))
    works = [fetch.result()["response"]["works"] for fetch in fetchs]

    def _works() -> Generator[Dict[str, Any], None, None]:
        """Generate work from works."""
        for page in works:
            for work in page:
                yield work

    with tqdm(total = len([_ for _ in _works()])) as t:
        tasks = [
            asyncio.ensure_future(add_illust(work, stores, t))
            for work in _works()
        ]
        loop.run_until_complete(asyncio.wait(tasks))
    if SETTINGS["store"]:
        with open(SETTINGS["file"], "w") as f:
            for task in tasks:
                stores.add(task.result())
            for store in stores:
                if store:
                    f.write(str(store) + "\n")


if __name__ == "__main__":
    main()
