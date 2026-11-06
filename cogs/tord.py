import nextcord
from nextcord import *
from nextcord.ui import Button, button, View
from dotenv import load_dotenv
import unicodedata
import os
from os import system, remove
from PIL import ImageColor, Image, ImageDraw, ImageFont
import aiohttp
from humanfriendly import format_timespan
from requests import get, post
from bson import ObjectId
import patreon
from nextcord.ext import commands
import nextcord.utils
import uwuipy
import pymongo
import bson
import random
import requests
import json
import textwrap
import asyncio
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
# DISCONTINUED DUE TO MENTAL HEALTH
db = mongodb.femdom_cage
def convert_to_seconds(duration: str):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(duration[:-1]) * seconds_per_unit[duration[-1]]

class tord(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    
def setup(client):
    client.add_cog(tord(client))