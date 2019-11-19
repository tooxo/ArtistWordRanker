# ArtistWordRanker

![docker](https://img.shields.io/docker/build/tooxo/artist_word_ranker?style=flat-square)

_`See, what your favourite Artists talk about!`_

## Demo:
This service is currently hosted on: https://s.chulte.de/awr/

## Build Instructions

0. Have Docker and Docker-Compose installed. You don't? Have a look here: [win](https://runnable.com/docker/install-docker-on-windows-10), [linux](https://runnable.com/docker/install-docker-on-linux)
1. Rename `.env.example` to `.env`
2. Edit the values in `.env`. If you prefer not to use AWS-DynamoDB leave the AWS section completely as it is. The feature will be disabled.
 (The other keys are all neccessary at the moment.)
3. Startup the server with `docker-compose up`
4. Enjoy!

## Test Instructions
**To Be Done!**