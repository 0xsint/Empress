import nextcord
from nextcord import *
from nextcord.ui import Button, button, View
from dotenv import load_dotenv
import os
from nextcord.ext import commands
import nextcord.utils
import nextcord
import pymongo
from asyncio import sleep
import json
import pytz
import datetime
import aiohttp
load_dotenv(dotenv_path="/root/as.env")
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class timers(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    async def snipe_loop(bot: commands.Bot):
        await bot.wait_until_ready()
        while not bot.is_closed():
            for guild in bot.guilds:
                try:
                    now = datetime.datetime.now(pytz.timezone("UTC"))
                    snipes = db.messages.find({"guild": guild.id})

                    for snipe in snipes:
                        if snipe["duration"] <= 0:
                            db.messages.delete_one({"_id": snipe["_id"]})
                        else:
                            db.messages.update_one({"_id": snipe["_id"]}, {"$inc": {"duration": -1}})
                except Exception as e:
                    print(f"Error in snipe_loop for guild {guild.id}: {e}")
            await sleep(1) 
def setup(client):
    client.add_cog(timers(client))