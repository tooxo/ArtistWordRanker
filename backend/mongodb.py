from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from os import environ
import random
import string
import re

"""
Dynamodb Structure:

Tables: 
    - Lyrics
        - Lyrics grouped by albums keyed with the artist
        - Struct:
            Artist | Song | Lyrics
    - Album Art
        - Url for all album art by an artist.
        - Struct:
            Artist | Url

"""


class MongoDB:
    def __init__(self, connection_string: str):
        mongo_connection_string = connection_string
        self.mongo = AsyncIOMotorClient(mongo_connection_string)

        self.lyrics_database = self.mongo.awr
        self.lyrics_table: AsyncIOMotorCollection = \
            self.lyrics_database.get_collection(
                "lyrics")
        self.art_table: AsyncIOMotorCollection = \
            self.lyrics_database.get_collection(
                "album_art")
        self.output_table: AsyncIOMotorCollection = \
            self.lyrics_database.get_collection(
                "output")

    @staticmethod
    def _generate_failed_signature():
        s = ""
        for x in range(0, 3):
            s += random.choice(string.digits)
        s += "FA"
        for x in range(0, 3):
            s += random.choice(string.digits)
        s += "IL"
        for x in range(0, 3):
            s += random.choice(string.digits)
        s += "ED"
        for x in range(0, 3):
            s += random.choice(string.digits)
        return s

    @staticmethod
    def _detect_failed_signature(resp: str):
        regex = r"[\d]{2}FA[\d]{2}IL[\d]{2}ED[\d]{2}"
        return re.match(regex, resp) is not None

    async def _check_if_lyric_exists(self, artist_name: str, track: str):
        return (
            await self.lyrics_table.find_one(
                {"artist": artist_name, "track": track}
            )
            is not None
        )

    async def _check_if_album_art_exists(self, artist_name: str):
        return (
                   await self.art_table.find_one(
                       {"artist": artist_name}
                   )
               ) is not None

    async def insert_lyrics(
        self, artist_name: str, track: str, lyrics: str, failed=False
    ):
        if artist_name == "" or track == "" or lyrics == "":
            return
        if await self._check_if_lyric_exists(artist_name, track):
            if failed:
                await self.lyrics_table.insert_one(
                    {
                        "artist": artist_name.lower(),
                        "track": track.lower(),
                        "lyrics": self._generate_failed_signature(),
                    }
                )
                return
            await self.lyrics_table.find_one_and_update(
                {"artist": artist_name.lower(), "track": track.lower()},
                {"$set": {"lyrics": lyrics}},
            )
        else:
            await self.lyrics_table.insert_one(
                {
                    "artist": artist_name.lower(),
                    "track": track.lower(),
                    "lyrics": lyrics,
                }
            )

    async def get_lyrics(self, artist_name: str, track: str):
        item = await self.lyrics_table.find_one(
            {"artist": artist_name.lower(), "track": track.lower()}
        )
        if item is None:
            return item
        return item.get("lyrics", "")

    async def insert_album_art(self, artist_name: str, json: str):
        if artist_name == "" or json == "":
            return
        if await self._check_if_album_art_exists(artist_name.lower()):
            await self.art_table.find_one_and_update(
                {"artist": artist_name.lower()}, {"$set": {"json": json}}
            )
        else:
            await self.art_table.insert_one(
                {"artist": artist_name.lower(), "json": json}
            )

    async def get_album_art(self, artist_name: str):
        item = await self.art_table.find_one({"artist": artist_name.lower()})
        if not item or item.get("json", "") == "[]":
            return None
        return item.get("json", "")

    async def insert_finished(self, artist_name: str, url):
        await self.output_table.insert_one({"artist": artist_name, "url": url})
