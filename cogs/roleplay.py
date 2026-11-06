import nextcord
from os import getenv
from nextcord import *
from dotenv import load_dotenv
from requests import get
from nextcord.ext import commands
import nextcord
import json
import nextcord
from pymongo import MongoClient
db = MongoClient(getenv("MONGODB")).femdom_cage
class roleplay(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    @nextcord.slash_command(
            name="roleplay",
            description="Roleplay"
    )
    async def rp(self, ctx: Interaction):
        pass

    @rp.subcommand(name="bite", description="Bite a user")
    async def bite(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to bite", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/bite/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} bites {user.mention}! Ouch!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="hug", description="Hug a user!")
    async def hug(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to hug", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/hug/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} hugs {user.mention} tightly! Awww!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="kiss", description="Kiss a user")
    async def kiss(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to kiss", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/kiss/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} kisses {user.mention} passionately! hawt***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="cuddle", description="Cuddle a user tightly")
    async def cuddle(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to cuddle", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/cuddle/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} cuddles {user.mention} passionately! Cute!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="pet", description="Give a user lots of headpats")
    async def pet(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to headpat", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/headpat/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} gives {user.mention} lots of headpats! Cute!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="slap", description="Slap a user")
    async def slap(self,ctx: Interaction, user: Member = SlashOption(name="user", description="User to slap", required=True)):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/slap/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} slaps {user.mention}! Show some respect!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="poke", description="Poke a user")
    async def poke(self,ctx: Interaction, user: Member = SlashOption(required=True, description="User to poke")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/poke/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} pokes {user.mention}! Poke Poke***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="blush", description="Blush cutely")
    async def blush(self,ctx: Interaction):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/blush/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} blushes cutely! Awwww!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="wag", description="Wag your tail!")
    async def wag(self,ctx: Interaction):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/wag/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} wags their tail! They must be excited!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="purr", description="Purrrfect!")
    async def purr(self,ctx: Interaction):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/purr/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} purrs happily! :3***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="cry", description="Cry because you're sad! ;-;")
    async def cry(self,ctx: Interaction):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/cry/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} cries sadly...I hope they're okay!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="pout", description="....Hmph!")
    async def pout(self,ctx: Interaction):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/pout/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} pouts! ...Hmph!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="boop", description="Boop a user")
    async def boop(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to boop")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/boop/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} boops {user.mention}'s snoot! Boop Boop!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @rp.subcommand(name="tickle", description="Tickle a user")
    async def tickle(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to tickle")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/sfw/tickle/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} tickles {user.mention}! They can't stop laughing!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nextcord.slash_command(name="nsfw_rp", nsfw=True, description="NSFW module")
    async def nsfw_rp(self, ctx: Interaction):
        pass

    @nsfw_rp.subcommand(name="fuck", description="Fuck a user hard")
    async def fuck(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to fuck")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/fuck/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} fucks {user.mention}! It'll hurt to walk after you're through with them!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nsfw_rp.subcommand(name="gag",description="Gag a user")
    async def gagged(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to gag")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/gag/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} gags {user.mention}! Maybe this will shut them up finally!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nsfw_rp.subcommand(name="peg" ,description="Peg a user")
    async def peg(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to peg")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/pegging/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} pegs {user.mention}!  It'll hurt to walk after you're through with them!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nsfw_rp.subcommand(name="worship" ,description="Worship a user")
    async def worship(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to worship")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/worship/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} worships {user.mention}! They are on the floor where they belong!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nsfw_rp.subcommand(name="whip",description="Whip a user")
    async def whip(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to whip")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/whip/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} whips {user.mention}! I hope they can't sit down for weeks!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
    @nsfw_rp.subcommand(name="tie_up",description="Tie up a user")
    async def tieup(self,ctx: Interaction, user: Member = SlashOption(required=True, name="user", description="User to tie up")):
        clr = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = clr['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        r = get("https://static.sorceress.online/nsfw/tie_up/")
        image = json.loads(r.text)
        embed = Embed(color=int(c, 16),description=f"***{ctx.user.mention} ties up {user.mention}! Tell them to stop squirming, they're a horrible chair!***\r\n").set_image(url=image['path'])
        await ctx.response.send_message(embed=embed)
def setup(client):
    client.add_cog(roleplay(client))
