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
class feedback(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    @slash_command(name="feedback", description="Have feedback or a bug report? I'd love to hear it! Please enter your feedback")
    async def feedback(self, ctx: Interaction,type: Literal["Feedback", "Bug Report", "Rating", "Account data deletion"] = SlashOption(name="type", description="Type of feedback", required=True), message: str = SlashOption(name="message", description="Feedback message", required=True), anonymous: bool = SlashOption(name="anonymous", description="Anonymous message?", required=True),rating: Literal["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"] = SlashOption(name="rating", description="Rating", required=False)):
          if not rating:
                 rating = "Rating was not set."
          user = await self.client.fetch_user(int(os.getenv("OWNER")))
          await ctx.response.send_message(embed=Embed(description="Your feedback is very important to us! It has been sent to the bot owner!", color=0xffa4e4), ephemeral=True)
          name = ""
          if anonymous:
                name = "Anonymous User"
          else:
                if ctx.user.discriminator == "0":

                     name = ctx.user.name
                else:
                     name = f"{ctx.user.name}#{ctx.user.discriminator}"
          await user.send(embed=Embed(title=f"New message from {name}", description=f"{message}", color=0xffa4e4).add_field(name="Rating", value=rating, inline=True).add_field(name="Type:", value=type, inline=True))

def setup(client):
        client.add_cog(feedback(client))
