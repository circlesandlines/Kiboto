# Kiboto Server
A set of tools for controlling games with artificial intelligence, for the sake of live competition.

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

# [NEW] Recipes
Common workflows and helper scripts can be found here:

https://github.com/circlesandlines/KibotoRecipes

To set up complete end to end workflow - game client, server, bot - follow the instructions in the respective repos below

## Game client SDK

https://github.com/circlesandlines/KibotoGameSDK

## Bot SDK

https://github.com/circlesandlines/KibotoBotSDK

