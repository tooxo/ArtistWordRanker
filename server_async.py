import asyncio
import base64
import os
import random
import string
from urllib.parse import unquote

import aiohttp
import uvicorn

import fastapi
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from dynamodb import DynamoDB
from backend.lyrics import Lyrics
from backend.mongodb import MongoDB
from backend.sqlite import SQLite
from backend.spotify import Spotify

loop = asyncio.new_event_loop()
app = fastapi.FastAPI()

if os.environ.get("DATABASE", "MONGO") == "MONGO":
    database = MongoDB()
else:
    raise NotImplementedError
    # database = DynamoDB()

sqlite = loop.run_until_complete(SQLite.create())
lyrics = Lyrics(sqlite, database)
spotify = Spotify()

templates = Jinja2Templates(directory="templates")

app.mount("/css", StaticFiles(directory="frontend/css"), "static-css")
app.mount("/image", StaticFiles(directory="frontend/image"), "static-image")
app.mount("/js", StaticFiles(directory="frontend/js"), "static-js")


def generate_job_id():
    job_id = ""
    for x in range(0, 63):
        job_id += random.choice(string.ascii_letters)
    return job_id


@app.get("/")
async def root():
    with open("frontend/index.html") as file:
        return fastapi.Response(file.read())


@app.post("/api/generate_image")
async def generate_image(request: fastapi.Request):
    post_data: dict = await request.json()
    for item in ["artist", "image_url", "predefined_image"]:
        if item not in post_data.keys():
            return fastapi.Response("Invalid Request", 400)

    artist_id = post_data["artist"]
    image_url = post_data["image_url"]
    predefined_image = post_data["predefined_image"]

    job_id = generate_job_id()

    await sqlite.add_job(job_id)
    asyncio.ensure_future(
        lyrics.artist_to_image(job_id, artist_id, image_url, predefined_image)
    )

    return fastapi.Response(job_id)


@app.post("/api/image_status")
async def image_status(request: fastapi.Request):
    post_data: str = (await request.body()).decode()
    job = await sqlite.get_job(post_data)
    return job


@app.post("/api/album_art")
async def album_art(request: fastapi.Request):
    post_data: str = (await request.body()).decode()
    albums = await spotify.get_album_images(post_data)
    albums.extend(
        [
            ("Red Solid Square", "image/red_square.png",),
            ("Green Solid Square", "image/green_square.png",),
            ("Blue Solid Square", "image/blue_square.png",),
        ]
    )
    return templates.TemplateResponse(
        "carousel.html",
        {
            "request": request,
            "carousel": albums
        }
    )


@app.post("/api/search")
async def search(request: fastapi.Request):
    post_data: str = (await request.body()).decode()
    sea = await spotify.search_artist(post_data)

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "inserts": list(
                map(
                    lambda artist: (
                        artist["name"], artist["url"], artist["image"],
                        artist["id"]
                    ),
                    sea
                )
            )
        }
    )


@app.get("/api/download")
async def download_image(request: fastapi.Request):
    encoded = request.query_params.get("url")
    mime_type = base64.b64decode(
        request.query_params.get("mime", "aW1hZ2UvanBlZw==")
    ).decode()
    extension = request.query_params.get("ext", "jpg")
    filename = unquote(request.query_params.get("name", "image"))
    data = base64.b64decode(encoded)
    async with aiohttp.request("GET", data.decode("utf-8")) as g:
        content = await g.content.read()
        return fastapi.Response(
            content=content,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename = "{filename}.'
                                       f'{extension}"',
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(content))
            }
        )


if __name__ == "__main__":
    server = uvicorn.Server(
        uvicorn.Config(
            app, host="0.0.0.0", port=8888, loop="asyncio", debug=True,
            reload=True
        )
    )
    loop.run_until_complete(server.serve())
