import random
import re

import aiohttp
from asyncio_pool import AioPool
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_gradient_magnitude
import io
import base64

from backend.async_helpers import force_async
from backend import lyrics_extractor, spotify
from backend.sqlite import SQLite
from .mongodb import MongoDB


class Lyrics:
    def __init__(self, sqlite: SQLite, database: MongoDB):
        self.database = database
        self.spotify = spotify.Spotify()
        self.sqlite = sqlite

    @staticmethod
    def lyrics_to_words(lyr: str):
        lyr = lyr.upper()
        re.sub(r"[^A-Z]", "", lyr)
        return lyr

    async def _all_lyrics_helper(self, song, job_id):
        db_result = await self.database.get_lyrics(song[1], song[0])
        if db_result is not None:
            result = song[1], song[0], db_result
        else:
            result = await \
                lyrics_extractor.LyricsExtractor.extract_from_genius_lib(
                    song[0], song[1])
        await self.sqlite.increase_lyrics(job_id)
        return result

    async def _get_all_them_lyrics(self, artist_id, job_id):
        songs = await self.spotify.get_songs_by_artist(artist_id)
        await self.sqlite.edit_lyrics(job_id=job_id, step=0, _all=len(songs))
        futures = []
        async with AioPool(size=10) as pool:
            for song in songs:
                fut = await pool.spawn(
                    self._all_lyrics_helper(song, job_id))
                futures.append(fut)

        results = [f.result() for f in futures]

        await self.sqlite.edit_lyrics(job_id, step=len(results), done=True)
        return results, len(songs)

    async def get_all_lyrics_of_artist(self, job_id: str, artist_id: str):
        couples, length = await self._get_all_them_lyrics(
            artist_id=artist_id, job_id=job_id
        )

        countable = 0
        comb = ""

        print("Inserting into Database ...")

        for couple in couples:
            song = couple[0]
            artist = couple[1]
            lyrics = couple[2]

            if lyrics is None:
                # skip using the db for now, it wont be accessed anyways
                # await self.database.insert_lyrics(
                #     artist_name=artist, track=song, lyrics="", failed=True
                # )
                continue
            countable += 1
            await self.database.insert_lyrics(
                artist_name=artist, track=song, lyrics=lyrics
            )
            comb += lyrics

        print(countable, "/", length)

        return comb

    @staticmethod
    def image_to_base64(image: Image):
        """
        Encodes an image to a base64 string
        :param image: PIL image input
        :return: base64 string
        :rtype: str
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue())

    async def upload_text(self, svg: str, artist_name: str):
        async with aiohttp.request(
            "POST",
            "https://www.klgrth.io/paste/new",
            data={
                "lang": "text",
                "text": svg,  # .encode("utf-8"),
                "expire": "-1",
                "password": "",
                "title": "",
            },
            allow_redirects=False
        ) as r:
            r: aiohttp.ClientResponse
            url = f"https://www.klgrth.io{r.headers.get('location')}/raw"
            # skip for now
            # await self.database.insert_finished(artist_name, url)
            return url

    async def artist_to_image(
        self,
        job_id: str,
        artist_id: str,
        image_url: str = None,
        predefined_image: bool = False,
    ):
        _lyr = await self.get_all_lyrics_of_artist(artist_id=artist_id,
                                                   job_id=job_id)

        img = None
        if not predefined_image:
            # the image is already there as base64 in image_url
            img = Image.open(io.BytesIO(base64.b64decode(image_url)))
        else:
            async with aiohttp.request("GET", image_url) as r:
                r: aiohttp.ClientResponse
                if r.status not in [200, 302]:
                    raise ConnectionError("Image not found.")
                img = Image.open(io.BytesIO(await r.read()))

        assert img is not None
        dim = min(img.size[0], img.size[1])

        img_color = np.array(img)
        img_mask = np.copy(img_color)
        img_mask[img_mask.sum(axis=2) == 0] = 255

        edg = np.nanmean(
            [
                gaussian_gradient_magnitude(img_color[:, :, i] / 255.0, 2)
                for i in range(3)
            ],
            axis=0,
        )
        img_mask[edg >= 0.05] = 255

        mul = 1500 / dim if 1500 > dim else 1

        wc = WordCloud(
            font_path="DroidSansMono.ttf",
            max_words=1500,
            min_font_size=0,
            background_color="white",
            #  mode="RGBA",
            mask=img_mask,
            random_state=random.randint(0, 100),
            relative_scaling=0,
            collocations=False,
            repeat=True,
            scale=mul,
        )

        await force_async(wc.generate, (), {"text": _lyr})
        img_colors = ImageColorGenerator(img_color)
        await force_async(wc.recolor, (), {"color_func": img_colors})
        svg = await force_async(wc.to_svg, (),
                                {"embed_font": True,
                                 "optimize_embedded_font": False})
        url = await self.upload_text(svg, artist_id)
        await self.sqlite.set_done(job_id, url)
        return url
