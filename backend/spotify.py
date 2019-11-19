import requests
import time
import base64
import threading
import multiprocessing.pool
from urllib.parse import quote
import requests_cache
import os

requests_cache.install_cache("requests.cache")


class Spotify:
    def __init__(self):
        self.client_id = os.environ.get("SPOTIFY_CLIENT", "")
        self.client_secret = os.environ.get("SPOTIFY_SECRET", "")
        self.token = ""

    def _invalidate_token(self):
        if self.token is not "":
            for x in range(1, 3000):
                try:
                    time.sleep(x)
                except InterruptedError:
                    self.token = ""
                    break
            self.token = ""

    def _request_token(self):
        if self.token is "":
            string = self.client_id + ":" + self.client_secret
            enc = base64.b64encode(string.encode())
            url = "https://accounts.spotify.com/api/token"
            header = {
                "Authorization": "Basic " + enc.decode(),
                "Content-Type": "application/x-www-form-urlencoded",
            }
            payload = "grant_type=client_credentials&undefined="
            with requests.post(url=url, headers=header, data=payload) as p:
                self.token = p.json().get("access_token")
            threading.Thread(target=self._invalidate_token).start()
            return self.token
        else:
            return self.token

    def research_artist(self, artist_name):
        token = self._request_token()
        base_url = "https://api.spotify.com/v1/search"
        header = {"Authorization": "Bearer " + token}
        try:
            with requests.get(
                url=base_url + "?type=artist&limit=1&q=" + quote(artist_name),
                headers=header,
            ) as g:
                return g.json()["artists"]["items"][0]["id"]
        except KeyError:
            return None

    def search_artist(self, query: str):
        token = self._request_token()
        base_url = "https://api.spotify.com/v1/search"
        header = {"Authorization": "Bearer " + token}
        try:
            with requests.get(
                url=base_url + "?type=artist&limit=10&q=" + quote(query.lower()),
                headers=header,
            ) as g:
                d = []
                for artist in g.json()["artists"]["items"]:
                    try:
                        n = {
                            "name": artist["name"],
                            "url": artist["external_urls"]["spotify"],
                            "image": artist["images"][0]["url"],
                        }
                        d.append(n)
                    except IndexError:
                        pass
            return d
        except KeyError:
            return "[]"

    def _get_albums_from_id(self, artist_id):
        token = self._request_token()
        base_url = (
            "https://api.spotify.com/v1/artists/"
            + artist_id
            + "/albums?country=DE&include_groups=album,single&limit=50"
        )
        headers = {"Authorization": "Bearer " + token}
        try:
            albums = []
            with requests.get(url=base_url, headers=headers) as g:
                for album in g.json()["items"]:
                    albums.append(album["id"])
            return albums
        except KeyError:
            return None

    def get_all_albums(self, artist_name):
        if artist_name == "":
            return None
        artist_id = self.research_artist(artist_name)
        if artist_id is None:
            return None
        albums = self._get_albums_from_id(artist_id)
        return albums

    def _get_tracks_from_album(self, album_id):
        token = self._request_token()
        base_url = (
            "https://api.spotify.com/v1/albums/"
            + album_id
            + "/tracks?limit=50&market=DE"
        )
        headers = {"Authorization": "Bearer " + token}
        try:
            tracks = []
            with requests.get(url=base_url, headers=headers) as g:
                s = g.json()
                for song in s["items"]:
                    tracks.append((song["name"], song["artists"][0]["name"]))
            return tracks
        except KeyError or IndexError as e:
            return None

    def get_songs_by_artist(self, artist_name):
        songs = []
        albums = self.get_all_albums(artist_name)
        pool = multiprocessing.pool.ThreadPool(processes=3)
        _als = []
        if albums is not None:
            for album in albums:
                if album is not None:
                    _als.append(album)
        track_tracks = pool.map(self._get_tracks_from_album, _als)
        for track_list in track_tracks:
            songs += track_list
        return songs
