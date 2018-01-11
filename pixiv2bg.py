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
* date: Jan 11, 2018
* email: echo bmFzeXh4QGdtYWlsLmNvbQo= | base64 -D
* file: pixiv2bg.py
* license: MIT

Copyright © 2017 by Nasy. All Rights Reserved.
"""
import asyncio
import os
from typing import Any, Awaitable, Dict, List, Optional

import aiohttp
import uvloop
from tqdm import tqdm

import ujson as json
from config import settings

assert Awaitable
assert Optional

URL = "https://api.pixiv.moe/v1/ranking?page="
SETTINGS = settings()
WKS = List[Dict[str, Any]]


class Pixiv:
    """Crawer of pixiv, craw pictures of pixiv for backgrouds."""

    def _load(self) -> Dict[str, Any]:
        """Load stored pictures."""
        with open(SETTINGS["file"]) as s:
            return json.load(s)

    def __init__(self) -> None:
        """Initialize Pixiv."""
        self.loop = uvloop.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.sema = asyncio.Semaphore(5)
        self.works = []  # type: List[Awaitable[None]]
        self.fetchs = [
            asyncio.ensure_future(self._fetch_page(p), loop = self.loop)
            for p in range(1, 11)
        ]
        self.stores = self._load()
        self.tqdm = None  # type: Optional[tqdm]

    async def _illusts_filter(self, illusts: Dict[str, Any]) -> bool:
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

    async def _fetch_page(self, page: int = 1) -> None:
        """Fetch pixiv.moe page."""
        async with aiohttp.ClientSession() as session:
            async with session.get(URL + str(page),
                                   proxy = "http://127.0.0.1:6152") as res:
                content = await res.json()
                if content.get("status") == "success":
                    work = content["response"]["works"]
                    await self._get_urls(work)
                    self.tqdm.update()

    async def _get_urls(self, works) -> None:
        """Get urls from works."""
        for illust in works:
            if (((not self.stores) or
                 str(illust["work"]["id"]) not in self.stores) and
                    await self._illusts_filter(illust)):
                self.works.append(
                    asyncio.ensure_future(
                        self.fetch_illust(
                            illust["work"]["image_urls"]["large"],
                            illust["work"]["title"],
                            str(illust["work"]["id"]),
                        )
                    )
                )
                self.stores.update({str(illust["work"]["id"]): illust})

    async def fetch_illust(self, url: str, title: str, workid: str) -> None:
        """Fetch illusts."""
        async with aiohttp.ClientSession() as session:
            try:
                async with self.sema:
                    async with session.get(
                            url,
                            proxy = "http://127.0.0.1:6152",
                    ) as res:
                        try:
                            os.mkdir("pictures")
                        except FileExistsError:
                            pass
                        chunks = b""
                        while True:
                            chunk = await res.content.read(128)
                            if not chunk:
                                break
                            chunks = chunks + chunk
            except asyncio.TimeoutError:
                self.stores.pop(workid)
            fname = f"{title.replace('/','-')}.{url[-4:].split('.')[-1]}"
            n = 1
            while fname in os.listdir("pictures/"):
                fname = (
                    f"{title.replace('/','-')}{n:03}."
                    "{url[-4:].split('.')[-1]}"
                )
                n += 1
            with open("pictures/" + fname, "wb") as f:
                f.write(chunks)
            self.tqdm.update()

    def run(self) -> None:
        """Run this crawer."""
        self.tqdm = tqdm(total = 10)
        self.loop.run_until_complete(asyncio.wait(self.fetchs))
        self.tqdm.close()

        if not self.works:
            print("Nothing to fetch!")
            return

        print("Fetch urls finished!")

        self.tqdm = tqdm(total = len(self.works))
        self.loop.run_until_complete(asyncio.wait(self.works))
        self.tqdm.close()
        with open(SETTINGS["file"] + ".temp", "w") as f:
            json.dump(self.stores, f)
        os.replace(SETTINGS["file"] + ".temp", SETTINGS["file"])


def main() -> None:
    """Yooo, here is the main function."""
    pixiv = Pixiv()
    pixiv.run()


if __name__ == "__main__":
    main()
