import pymongo
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
    def __init__(self):
        mongo_connection_string = environ.get("MONGO_CONNECTION_STRING", "")
        self.mongo = pymongo.MongoClient(mongo_connection_string)

        self.lyrics_database = self.mongo.get_database("awr")
        self.lyrics_table = self.lyrics_database.get_collection("lyrics")
        self.art_table = self.lyrics_database.get_collection("album_art")

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

    def _check_if_lyric_exists(self, artist_name: str, track: str):
        return (
            self.lyrics_table.find_one({"artist": artist_name, "track": track})
            is not None
        )

    def _check_if_album_art_exists(self, artist_name: str):
        return self.art_table.find_one({"artist": artist_name}) is not None

    def insert_lyrics(self, artist_name: str, track: str, lyrics: str, failed=False):
        if artist_name == "" or track == "" or lyrics == "":
            return
        if self._check_if_lyric_exists(artist_name, track):
            if failed:
                self.lyrics_table.insert_one(
                    {
                        "artist": artist_name.lower(),
                        "track": track.lower(),
                        "lyrics": self._generate_failed_signature(),
                    }
                )
                return
            self.lyrics_table.find_one_and_update(
                {"artist": artist_name.lower(), "track": track.lower()},
                {"$set": {"lyrics": lyrics}},
            )
        else:
            self.lyrics_table.insert_one(
                {
                    "artist": artist_name.lower(),
                    "track": track.lower(),
                    "lyrics": lyrics,
                }
            )

    def get_lyrics(self, artist_name: str, track: str):
        item = self.lyrics_table.find_one(
            {"artist": artist_name.lower(), "track": track.lower()}
        )
        if item is None:
            return item
        return item.get("lyrics", "")

    def insert_album_art(self, artist_name: str, json: str):
        if artist_name == "" or json == "":
            return
        if self._check_if_album_art_exists(artist_name.lower()):
            self.art_table.find_one_and_update(
                {"artist": artist_name.lower()}, {"$set": {"json": json}}
            )
        else:
            self.art_table.insert_one({"artist": artist_name.lower(), "json": json})

    def get_album_art(self, artist_name: str):
        item = self.art_table.find_one(
            {"artist": artist_name.lower()}
        )
        if item is None:
            return item
        return item.get("json", "")
