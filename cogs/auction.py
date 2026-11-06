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
# THIS WAS DISCONTINUED DUE TO MENTAL HEALTH
def random_int(start: int, finish: int):
    return range(start, finish)
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
def convert_to_seconds(duration: str):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(duration[:-1]) * seconds_per_unit[duration[-1]]

class auction(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    @nextcord.slash_command(
        name="auction",
        description="Auction function",
        nsfw=True,
        guild_ids=[1242612502895001600]
    )
    async def auction(self, ctx: Interaction):
        pass
    @auction.subcommand(
            name="bid", 
            description="Add to the bid of a auction"
    )
    async def bid(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to bid on", required=True), amount: int = SlashOption(name="amount_to_bid", description="Amount of currency to bid", required=True)):
        color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        role_ids = []
        claim_check = db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
        domme_check = db.claims.find_one({"guild": ctx.guild.id, "domme": user.id})
        config_sd = db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
        config = db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        config_s = db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_d = db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        domme_check = db.claims.find_one({"guild": ctx.guild.id, "domme": ctx.user.id})
        d = False
        s = False
        swtch = False
        sub = False
        slut = False
        auc = db.auctions.find_one({"user": user.id, "guild": ctx.guild.id})
        if "-" in str(amount):
            await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't bid with negatives!", color=int(c, 0)))
            return
        elif "+" in str(amount):
            await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't have this character when bidding!", color=int(c, 0)))
            return
        elif "." in str(amount):
            await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't bid with decimals!", color=int(c, 0)))
            return
        elif int(amount) == 0:
            await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't bid with only the amount of 0!", color=0xffb6c1))
            return
        result_a = db.currency.find_one({"guild": ctx.guild.id})
        user_bal_q = {"user": ctx.user.id, "guild": ctx.guild.id}
        bal = db.balance.find_one(user_bal_q)
        new_bal = bal['balance'] - int(amount + auc.get("bid", 0))
        if "-" in str(new_bal):
            await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! Insufficient funds to bid!", color=int(c, 0)))
        else:
            auction = db.auctions.find_one_and_update({"user": user.id, "guild": ctx.guild.id}, {"$inc": {"bid": amount}})
            if not auction:
                await ctx.response.send_message(embed=nextcord.Embed(title="Auction not found!", color=int(c, 0)))
                return
            else:
                chan = await ctx.guild.fetch_channel(auction['channel'])
                msg = await chan.fetch_message(auction['msg_id'])
                if not msg: 
                    await ctx.response.send_message(embed=nextcord.Embed(title="Auction not found!", color=int(c, 0)))
                    return
                else:
                    await ctx.response.send_message(embed=Embed(title="Auction updated", description=f"{user.mention}'s auction has now been updated to {int(int(auc['bid']) + amount)} {result_a['result']}"))
                    if auction['image']:
                        await msg.edit(embed=Embed(description=f"***Auction of <@{user.id}>!***", color=int(c, 16)).add_field(name="Info", value=auction['info'], inline=False).add_field(name="Current bid", value=f"{int(auction['bid'] + amount)} {result_a['result']}", inline=False).add_field(name="Role", value=auction['role'], inline=False).set_image(f"attachment://auction_{user.id}{auction['domme']}{ctx.guild.id}.png"))
                    else:
                        await msg.edit(embed=Embed(description=f"***Auction of <@{user.id}>!***", color=int(c, 16)).add_field(name="Info", value=auction['info'], inline=False).add_field(name="Current bid", value=f"{int(auction['bid'] + amount)} {result_a['result']}", inline=False).add_field(name="Role", value=auction['role'], inline=False))
    @auction.subcommand(
        name="sell",
        description="Sell a Domme/sub for auction"
    )
    async def sell_auction(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to auction", required=True), start: int = SlashOption(name="start", description="The starting bid", required=True), info: str = SlashOption(name="description", description="Information about the user being auctioned", required=True), pic: Attachment = SlashOption(name="image_of_character_or_user", description="Image of yourself or your OC", required=False)):
        domme_roles = []
        color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        role_ids = []
        claim_check = db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
        domme_check = db.claims.find_one({"guild": ctx.guild.id, "domme": user.id})
        config_sd = db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
        config = db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        config_s = db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_d = db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        curre = [domme_roles.append(r.id) for r in ctx.user.roles]
        curr = [role_ids.append(role.id) for role in user.roles]
        domme_check = db.claims.find_one({"guild": ctx.guild.id, "domme": ctx.user.id})
        d = False
        s = False
        swtch = False
        sub = False
        slut = False
        result_a = db.currency.find_one({"guild": ctx.guild.id})
        try:
            if config_d['value'] in role_ids:
                if config_d['value'] in role_ids and config_d['value'] not in domme_roles:
                    await ctx.response.send_message(embed=Embed(
                    title="Ew no.",
                    description=f"Only {user.mention} can auction themselves, slut.",
                    color=int(c, 16)
                ), ephemeral=True)
                    return
                d = True
            if config_ss['value'] in role_ids or config_sd['value'] in role_ids or config_s['value'] in role_ids:
                if config['value'] in domme_roles:
                    await ctx.response.send_message(embed=Embed(
                    title="Ew no.",
                    description=f"Only switches and Dommes can auction {user.mention}, slut.",
                    color=int(c, 16)
                ), ephemeral=True)
                    return
                if claim_check:
                    if claim_check['domme'] == ctx.user.id:
                        sub = True
                    else:

                        await ctx.response.send_message(embed=Embed(
                    title="Ew no.",
                    description=f"Only <@{claim_check['domme']}> can auction {user.mention}.",
                    color=int(c, 16)
                    ), ephemeral=True)
                        return
                else:
                    if config.get("value") in role_ids:
                        sub = True
                    if config_s.get("value") in role_ids or config_sd.get("value") in role_ids or config_ss.get("value") in role_ids:
                        swtch = True

                if claim_check:
                    if claim_check['domme'] == ctx.user.id:
                        sub = True
                    else:
                        await ctx.response.send_message(embed=Embed(
                    title="Ew no.",
                    description=f"Only <@{claim_check['domme']}> can auction {user.mention}.",
                    color=int(c, 16)
                    ), ephemeral=True)
                        return
                else:
                    slut = True
            else:
                sub = True
            username = ""
            if user.nick:
                username = user.nick
            else:
                username = user.global_name
            if sub:
                call_view = None
                if pic:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="sub", info=info, image=pic.read())
                else:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="sub", info=info)
                await ctx.response.send_message(content=f"{user.mention}", embed=Embed(title=f"Auction of {username}", description=f"Hey Goddess are you sure you want to auction your sub for the starting bid of {start} {result_a['result']}", color=int(c, 16)),view=call_view, ephemeral=True)
                await call_view.wait()
                if call_view.Value == True:
                    return
            if d:
                call_view = None
                if pic:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="domme", info=info, image=pic.read())
                else:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="domme", info=info)
                await ctx.response.send_message(content=f"{user.mention}", embed=Embed(title=f"Auction of {username}", description=f"Hey Goddess are you sure you want to auction yourself for the starting bid of {start} {result_a['result']}", color=int(c, 16)),view=call_view, ephemeral=True)
                await call_view.wait()
                if call_view.Value == True:
                    return
            if slut:
                call_view = None
                if pic:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="unclaimed sub", info=info, image=pic.read())
                else:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="unclaimed sub", info=info)
                await ctx.response.send_message(content=f"{user.mention}", embed=Embed(title=f"Auction of {username}", description=f"Hey slut are you sure you want to auction yourself for the starting bid of {start} {result_a['result']}", color=int(c, 16)),view=call_view, ephemeral=True)
                await call_view.wait()
                if call_view.Value == True:
                    return
            if swtch:
                call_view = None
                if pic:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="switch", info=info, image=pic.read())
                else:
                    call_view = consent_view(user=user, domme=ctx.user, start_bid=start, role_type="switch", info=info)
                await ctx.response.send_message(content=f"{user.mention}", embed=Embed(title=f"Auction of {username}", description=f"Hey Goddess/slut are you sure you want to auction your sub for the starting bid of {start} {result_a['result']}", color=int(c, 16)),view=call_view)
                await call_view.wait()
                if call_view.Value == True:
                    return
        except Exception as e:
            await ctx.response.send_message(embed=Embed(description=f"**I encountered an error {e}.**"), ephemeral=True)
            print (e)
            return
class consent_view(View):
    def __init__(self, user, domme, start_bid, role_type, info, image = None):
        super().__init__(timeout=600)
        self.user = user
        self.domme = domme
        self.start_bid = start_bid
        self.role_type = role_type
        self.info = info
        self.image = image
        self.Value = False
    @button(style=ButtonStyle.green, custom_id="yes", label="I'd love to!", emoji="<:yes:1138216175264870400>")
    async def yes_button(self, button: Button, ctx: Interaction):
        color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        user = self.user
        button.disabled = True
        domme = self.domme
        if user != ctx.user:
            return
        result = db.claims.find_one({"guild": ctx.guild.id, "domme": domme.id, "submissives": {"$in":[user.id]}})
        domme_roles = []
        role_ids = []
        result_a = db.currency.find_one({"guild": ctx.guild.id})
        claim_check = db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
        domme_check = db.claims.find_one({"guild": ctx.guild.id, "domme": domme.id})
        config_sd = db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
        config = db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        config_s = db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_d = db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        curre = [domme_roles.append(r.id) for r in ctx.user.roles]
        curr = [role_ids.append(role.id) for role in user.roles]
        d = False
        s = False
        active = False
        if self.image:
            fp = open(f"auction_{self.user.id}{self.domme.id}{ctx.guild.id}.png", "wb")
            fp.write(self.image)
            fp.close()
        sub = False
        if not claim_check and self.role_type == "sub":
            active = True
            sub = True
        elif domme_check and not claim_check and self.role_type == "domme":
            s = True
            active = True
        else:
            d = True
            active = True
        if claim_check:
            await ctx.response.send_message(embed=Embed(description=f"It seems {user.mention} has already been claimed by: <@{claim_check['domme']}>!", color=int(c, 16)))
            return

        if not result:
            if sub and active and claim_check and claim_check.get("domme") != self.domme.id:
                await ctx.response.send_message(embed=Embed(description=f"***Unable to complete request, sub is already owned***", color=int(c, 16)))
                self.Value = True
                return
            else:
                pass
        if self.image:
            msg = await ctx.response.send_message(embed=Embed(description=f"***Auction of <@{user.id}>!***", color=int(c, 16)).add_field(name="Info", value=self.info, inline=False).add_field(name="Current bid", value=f"{self.start_bid} {result_a['result']}", inline=False).add_field(name="Role", value=self.role_type, inline=False).set_image(url=f"attachment://auction_{user.id}{domme.id}{ctx.guild.id}.png"))
            message = await msg.fetch()
            db.auctions.update_one({"user": user.id, "guild": ctx.guild.id, "channel": ctx.channel.id, "msg_id": message.id},{"$set": {"bid": self.start_bid, "info": self.info, "image": self.image, "domme": self.domme.id, "role": self.role_type}} , upsert=True)
            self.Value = True
            return
        else:
            msg = await ctx.response.send_message(embed=Embed(description=f"***Auction of <@{user.id}>!***", color=int(c, 16)).add_field(name="Info", value=self.info, inline=False).add_field(name="Current bid", value=f"{self.start_bid} {result_a['result']}", inline=False).add_field(name="Role", value=self.role_type, inline=False))
            message = await msg.fetch()
            db.auctions.update_one({"user": user.id, "guild": ctx.guild.id, "channel": ctx.channel.id, "msg_id": message.id},{"$set": {"bid": self.start_bid, "info": self.info, "image": self.image, "domme": self.domme.id, "role": self.role_type}} , upsert=True)
            self.Value = True
            return
    @button(style=ButtonStyle.red, custom_id="no", label="No way!", emoji="<:no:1139098428715040768>")
    async def no_button(self, button: Button, ctx: Interaction):
        color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        button.disabled = True
        if self.user != ctx.user:
            return
        await ctx.response.send_message(embed=Embed(title="Declined!", description="<a:prison_loading:1138685852550172703> Ownership has been declined, canceling..", color=int(c, 16)))
        self.Value = True
        return True
    @button(style=ButtonStyle.blurple, custom_id="cancel", label="Cancel", emoji="<:no:1139098428715040768>")
    async def cancel_button(self, button: Button, ctx: Interaction):
        color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        button.disabled = True
        if self.domme != ctx.user:
            return
        await ctx.response.edit_message(embed=Embed(title="Cancelled!", description="<a:prison_loading:1138685852550172703> Ownership has been cancelled..", color=int(c, 16)))
        self.value = True
        return False
def setup(client):
    client.add_cog(auction(client))
