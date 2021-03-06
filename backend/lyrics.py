import random
import re
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_gradient_magnitude
import requests
import io
import base64
from backend import dynamodb, lyrics_extractor, spotify, mongodb
import multiprocessing
import multiprocessing.pool
from backend.sqlite import SQLite
import os
from backend.lyrics_cleanup import LyricsCleanup


class Lyrics:
    def __init__(self):
        if os.environ.get("DATABASE", "MONGO") == "MONGO":
            self.database = mongodb.MongoDB()
        else:
            self.database = dynamodb.DynamoDB()
        self.spotify = spotify.Spotify()
        self.lyrics = lyrics_extractor.LyricsExtractor()
        self.sqlite = SQLite()
        self.lyrics_extractor = lyrics_extractor.LyricsExtractor()
        self.api_key_img_bb = os.environ.get("IMG_BB", "")
        self.api_key_imgur = os.environ.get("IMGUR", "")

    @staticmethod
    def lyrics_to_words(lyr: str):
        lyr = lyr.upper()
        re.sub(r"[^A-Z]", "", lyr)
        return lyr

    def _multi_helper(self, args):
        return self.lyrics_extractor.extract_random(*args)

    def _get_all_them_lyrics(self, artist_name, job_id):
        songs = self.spotify.get_songs_by_artist(artist_name)
        sqlite = SQLite()
        sqlite.edit_lyrics(job_id=job_id, step=0, _all=len(songs))
        combo = []
        for song in songs:
            t = (song[0], song[1], job_id)
            combo.append(t)
        pool = multiprocessing.pool.ThreadPool(processes=10)
        response = pool.map(self._multi_helper, combo)
        sqlite.edit_lyrics(job_id, step=len(response), done=True)
        return response, len(songs)

    def get_all_lyrics_of_artist(self, job_id: str, artist_name: str):
        couples, length = self._get_all_them_lyrics(
            artist_name=artist_name, job_id=job_id
        )

        countable = 0

        comb = ""

        for couple in couples:
            song = couple[0]
            artist = couple[1]
            lyrics = couple[2]
            if lyrics is None:
                self.database.insert_lyrics(
                    artist_name=artist, track=song, lyrics="", failed=True
                )
                continue
            lyrics = LyricsCleanup.clean_up(lyrics)
            countable += 1
            self.database.insert_lyrics(
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

    def upload_to_img_bb(self, base64_e: str, artist_name: str):
        """
        Uploads an image to img_bb
        :param base64_e: Base64 representation of image
        :param artist_name: name of the artist
        :return: url of the image
        """

        base_url = "https://api.imgbb.com/1/upload?key="
        with requests.post(
            base_url + self.api_key_img_bb,
            data={"image": base64_e, "name": artist_name},
        ) as post:
            response = post.json()
        return response.get("data", {"url", ""}).get("url", "")

    def upload_to_imgur(self, base64_e: str, artist_name: str):
        """
        Uploads an image to imgur
        :param base64_e:
        :param artist_name: not used
        :return:
        """
        base_url = "https://api.imgur.com/3/upload"
        with requests.post(
            url=base_url,
            data=base64_e,
            headers={"Authorization": "Client-ID " + self.api_key_imgur},
        ) as p:
            response = p.json()
            if response.get("success", False):
                return response["data"]["link"]

    @staticmethod
    def upload_to_file_io(base64_e: str, artist_name: str):
        """
        Uploads an image to file.io
        :param base64_e:
        :param artist_name:
        :return:
        """
        base_url = "https://file.io/?expires=1w"
        with requests.post(
            base_url,
            data={"file": artist_name + ".jpg"},
            files={
                "file": (artist_name + ".jpg", base64.decodebytes(base64_e))
            },
        ) as p:
            response = p.json()
            if response.get("success", False):
                return response.get("link", "")

    def upload_image(self, image: Image, artist_name: str):
        image_upload_pool = [
            # self.upload_to_img_bb,
            self.upload_to_imgur
        ]
        base64_e = self.image_to_base64(image)
        url = random.choice(image_upload_pool)(base64_e, artist_name)
        self.database.insert_finished(artist_name, url)
        return url

    def upload_text(self, svg: str, artist_name: str):
        with requests.post(
            "https://hastebin.com/documents", data=svg.encode("utf-8")
        ) as r:
            url = f"https://hastebin.com/raw/{r.json()['key']}"
            self.database.insert_finished(artist_name, url)
            return url

    def artist_to_image(
        self,
        job_id: str,
        artist: str,
        image_url: str = None,
        predefined_image: bool = False,
    ):
        _lyr = self.get_all_lyrics_of_artist(artist_name=artist, job_id=job_id)

        img = None
        if not predefined_image:
            # the image is already there as base64 in image_url
            img = Image.open(io.BytesIO(base64.b64decode(image_url)))
        else:
            with requests.get(image_url) as r:
                if r.status_code is not 200 and r.status_code is not 302:
                    raise ConnectionError("Image not found.")
                img = Image.open(io.BytesIO(r.content))

        assert img is not None
        dim = min(img.size[0], img.size[1])

        img_color = np.array(img)
        img_mask = np.copy(img_color)
        img_mask[img_mask.sum(axis=2) == 0] = 255

        edg = np.mean(
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

        wc.generate(text=_lyr)
        img_colors = ImageColorGenerator(img_color)
        wc.recolor(color_func=img_colors)
        svg = wc.to_svg(embed_font=True, optimize_embedded_font=True)
        url = self.upload_text(svg, artist)
        SQLite().set_done(job_id, url)
        return url
