import nextcord
from nextcord import *
from dotenv import load_dotenv
from requests import post
import pymongo
from nextcord.ext import commands
import json
import os
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class p(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @nextcord.slash_command(
        name="porn",
        description="Porn Module",
        nsfw=True
    )
    async def porn(self, ctx: Interaction):
        pass
    
    @porn.subcommand(
        name="search",
        description="Search for porn",
    )
    async def search(self, ctx: Interaction, query: str = SlashOption(name="query", description="Search query for pornhub's api to read", required=True, default="Femdom")):
        if db.options.find_one({"guild": ctx.guild.id, "porn": True}):
            msg = await ctx.response.send_message("Fetching porn..")
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            try:
                uri_builder = f"https://sorceress.online/porn/api/search_one"
                req = post(uri_builder, data={"query": query}).text
                print (req)
                req = json.loads(req)
                print (req)
                stars = None
                await msg.edit("Searching..Please wait this may take a bit..")
                embed_builder = Embed(
                title=f"{req['title']}",
                description=f"\r\n{req['category']}\r\n\r\n **Pornhub ID:** {req['key']}",
                url=req['url'],
                color=int(c, 0)
                ).set_image(url=f"{req['gif']}")
                await msg.edit(content="",embed=embed_builder)
            except Exception as e:
            
                print (e)
                await msg.edit(content="", embed=Embed(title="Something went wrong with your request!", color=int(c, 0)))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for porn, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
def setup(client):
    client.add_cog(p(client))
