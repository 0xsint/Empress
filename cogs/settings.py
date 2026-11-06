import nextcord
from nextcord import *
from nextcord.ui import Button, button, View
from dotenv import load_dotenv
import os
from nextcord.ext import commands
import nextcord.utils
import nextcord
import pymongo
import json
import pytz
import datetime
import aiohttp
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class settings(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    
    @nextcord.slash_command(
        name="settings",
        description="Settings module",
        default_member_permissions=Permissions(administrator=True)
    )
    async def setting(self, ctx: Interaction):
        pass
    @setting.subcommand(
        name="enable",
        description="Enable a configuration setting"
    )
    async def enable(self, ctx: Interaction, option: Literal["BDSM", "Economy", "Levels", "Porn", "Images", "Auctions"] = SlashOption(name="option", description="Option to enable")):
        db.options.update_one({"guild": ctx.guild.id}, {"$set": {option.lower(): True}}, upsert=True)
        await ctx.response.send_message(embed=Embed(
            title=f"Config key ``{option}`` has been set to enabled.",
            color=0xffa4e4            
        ))
    @setting.subcommand(
        name="disable",
        description="Disable a configuration setting"
    )
    async def disable(self, ctx: Interaction, option: Literal["BDSM", "Economy", "Levels", "Porn", "Images", "Auctions"] = SlashOption(name="option", description="Option to disable")):
        db.options.update_one({"guild": ctx.guild.id}, {"$set": {option.lower(): False}}, upsert=True)
        await ctx.response.send_message(embed=Embed(
            title=f"Config key ``{option}`` has been set to disabled.",
            color=0xffa4e4            
        ))
def setup(client):
    client.add_cog(settings(client))