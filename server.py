from flask import (
    Flask,
    Response,
    request,
    redirect,
    send_file,
    send_from_directory,
)
from backend.lyrics import Lyrics
from backend.album_art_extraction import AlbumArt
from backend.spotify import Spotify
import backend.generator
import json
import bjoern
import os
from backend.sqlite import SQLite
import string
import random
import threading
import requests
import io
import base64
from queue import Queue


class Server:
    def __init__(self):
        self.app = Flask(__name__)
        self.add_routes()
        self.lyrics = Lyrics()
        self.album_art = AlbumArt()
        self.spotify = Spotify()
        self.sqlite = SQLite()
        self.word_cloud_queue = Queue(maxsize=10000)

    @staticmethod
    def generate_job_id():
        job_id = ""
        for x in range(0, 63):
            job_id += random.choice(string.ascii_letters)
        return job_id

    def start_tuple(self, job_id, artist, image_url, predefined_image):
        return self.lyrics.artist_to_image(
            job_id, artist, image_url, predefined_image
        )

    def queue_task(self):
        try:
            while True:
                (
                    job_id,
                    artist,
                    image_url,
                    predefined_image,
                ) = self.word_cloud_queue.get(block=True)
                self.start_tuple(job_id, artist, image_url, predefined_image)
        except (KeyboardInterrupt, SystemExit):
            pass

    def add_routes(self):
        @self.app.route("/api/generate_image", methods=["POST"])
        def image_generation():
            post_data = request.get_json(force=True)
            artist = post_data["artist"]
            image_url = post_data["image_url"]
            predefined_image = post_data["predefined_image"]

            job_id = self.generate_job_id()
            t = (job_id, artist, image_url, predefined_image)
            self.word_cloud_queue.put_nowait(t)
            self.sqlite.add_job(job_id)
            return job_id

        @self.app.route("/api/image_status", methods=["POST"])
        def image_status():
            post_data = request.get_data().decode()
            job = self.sqlite.get_job(post_data)
            return json.dumps(job)

        # @self.app.route("/api/album_art", methods=["POST"])
        def album_art_old():
            post_data = request.data.decode()
            artist = self.album_art.get_artist(post_data)
            d = json.loads(artist)
            if len(d) is 0:
                d = backend.generator.no_image_default
            text = ""
            for image in d:
                text += backend.generator.carousel_generator(
                    image["url"].replace("100x100bb", "300x300bb"),
                    image["title"],
                )
            return Response(text)

        @self.app.route("/api/album_art", methods=["POST"])
        def album_art():
            post_data = request.data.decode()
            albums = self.spotify.get_album_images(post_data)
            albums.extend(backend.generator.no_image_default)
            text = ""
            for album in albums:
                text += backend.generator.carousel_generator(
                    album[1],
                    album[0]
                )
            return Response(text)

        @self.app.route("/api/search", methods=["POST"])
        def search():
            post_data = request.data.decode()
            sea = self.spotify.search_artist(post_data)
            big_insert = (
                '<a class="waves-effect waves-light btn" '
                'id="search_back" href="javascript:search_back()" '
                'style="display:none">Back</a>'
            )
            for artist in sea:
                insert = backend.generator.search_generator(
                    artist["name"], artist["url"], artist["image"]
                )
                big_insert += insert
            return Response(big_insert)

        @self.app.route("/api/download", methods=["GET"])
        def download_image():
            encoded = request.args.get("url")
            mime_type = base64.b64decode(
                request.args.get("mime", "aW1hZ2UvanBlZw==")
            ).decode()
            extension = request.args.get("ext", "jpg")
            data = base64.b64decode(encoded)
            with requests.get(url=data) as g:
                return send_file(
                    io.BytesIO(g.content),
                    mimetype=mime_type,
                    as_attachment=True,
                    attachment_filename=f"image.{extension}",
                )

        # -- Frontend --
        @self.app.route("/")
        def index():
            return send_file("./frontend/index.html")

        @self.app.route("/css/style.css")
        def style_css():
            return send_file("./frontend/css/style.css")

        @self.app.route("/js/init.js")
        def init_js():
            return send_file("./frontend/js/init.js")

        @self.app.route("/image/<path:path>")
        def send_js(path):
            return send_from_directory("frontend/image", path)

    def start_up(self):
        self.sqlite.initiate_database()
        threading.Thread(target=self.queue_task).start()
        if os.environ.get("DEBUG", "False") == "False":
            bjoern.listen(
                self.app, host="0.0.0.0", port=int(os.environ.get("PORT", 8888))
            )
            bjoern.run()
        else:
            self.app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8888)))


if __name__ == "__main__":
    s = Server()
    s.start_up()
