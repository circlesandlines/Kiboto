# Kiboto Server
A set of tools for controlling games with artificial intelligence, for the sake of live competition.

## Status
Kiboto is currently in a pre-release state. Stay tuned to get installation instructions, environment setup, and tutorials

## TODO for 1.0 release
- [x] initialize game sessions based on game client requests
- [x] back up sessions in redis
- [x] accept bot session registration
- [ ] solidify edge-cases
- [ ] formal tests
- [ ] formal documentation


## Requirements:

- python 2.7, 3.2, 3.3, and 3.4
- tornado
- tornadis (async redis client)
- redis (sync redis client)
- local redis server running

## Install

Install and run redis server:
http://redis.io/topics/quickstart

At the moment, there is no official Kiboto release, so just clone the repo
```
git clone git@github.com:circlesandlines/Kiboto.git
cd Kiboto
```

Kiboto has only python package dependencies, so you can install it entirely with pip
```
pip install -r requirements.txt
```

Copy the sample config and modify it as your own. At the moment, you only need to add the port:
```
cp conf/server_sample.config conf/server.config
vim conf/server.config
```

Start up the server:
```
# cd to project root directory
python kiboto.py
```

To set up complete end to end workflow - game client, server, bot - follow the instructions in the respective repos below

## Game client SDK

https://github.com/circlesandlines/KibotoGameSDK

## Bot SDK

https://github.com/circlesandlines/KibotoBotSDK

