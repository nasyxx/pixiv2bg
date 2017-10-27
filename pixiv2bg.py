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
from typing import Any, Dict, Generator

import aiohttp
import uvloop
from tqdm import tqdm

import ujson as json
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
        try:
            async with session.get(url,
                                   proxy = "http://127.0.0.1:6152") as res:
                try:
                    os.mkdir("pictures")
                except FileExistsError:
                    pass
                chunks = b""
                while True:
                    chunk = await res.content.read(5)
                    if not chunk:
                        break
                    chunks = chunks + chunk
        except asyncio.TimeoutError:
            return
        with open((f"pictures/{title.replace('/','-')}."
                   f"{url[-4:].split('.')[-1]}"), "wb") as f:
            f.write(chunks)


async def add_illust(illust: Dict[str, Any], stores: Dict[str, Any],
                     t: Any) -> Dict[str, Any]:
    """Add illusts."""
    if ((not stores or str(illust["work"]["id"]) not in stores) and
            await illusts_filter(illust)):
        try:
            await fetch_illust(
                illust["work"]["image_urls"]["large"], illust["work"]["title"]
            )
            t.update()
            return illust["work"]
        except aiohttp.client_exceptions.ServerDisconnectedError:
            pass
    t.update()
    return {"id": None}


def main() -> None:
    """Run this task."""
    stores = {}  # type: Dict[str, Any]
    if SETTINGS.get("store", True):
        try:
            with open(SETTINGS["file"]) as s:
                stores = json.load(s)  # pylint: disable=E1101
        except FileNotFoundError:
            pass
        except ValueError:
            pass
    else:
        pass

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
        with open(SETTINGS["file"] + ".temp", "w") as f:
            for task in tasks:
                result = task.result()
                if result["id"]:
                    stores[result["id"]] = result
            json.dump(stores, f)  # pylint: disable=E1101
        os.replace(SETTINGS["file"] + ".temp", SETTINGS["file"])


if __name__ == "__main__":
    main()
