
import requests
import nextcord
from nextcord import *
from nextcord.ui import Button, button, View
from dotenv import load_dotenv
import unicodedata
import motor.motor_asyncio
import os
import requests
from os import system, remove
import re
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
import io
import aiofiles
import aiohttp
import random
import requests
import json
import textwrap
import asyncio
load_dotenv()
mongodb = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
def convert_to_seconds(duration: str):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    return int(duration[:-1]) * seconds_per_unit[duration[-1]]


class bdsm(commands.Cog):
    def __init__(self, client):
        self.client = client

    @nextcord.slash_command(
        name="task",
        description="Task module",
        nsfw=True
    )
    async def task_comm(self, ctx: Interaction):
        pass

    @task_comm.subcommand(
        name="list",
        description="Get a list of tasks on a sub"
    )
    async def task_lst(self, ctx: Interaction, user: Member = SlashOption(name="user", description="Sub to check tasks of", required=False)):
        opt = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not opt:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for BDSM. Ask the owner to use `/settings enable`.",
                color=0xffa4e4
            ), ephemeral=True)
            return

        user = user or ctx.user
        msg = await ctx.response.send_message("Running... please wait...")
        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color["string"]
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else f"0x{c}"

        try:
            task_exists = await db.task_list.find_one({"sub": user.id, "guild": ctx.guild.id})
            if not task_exists:
                await msg.edit(content="", embed=Embed(
                    title="No tasks found",
                    description=f"No tasks associated with {user.mention}",
                    color=int(c, 16)
                ))
                return

            results = ""
            async for task in db.task_list.find({"sub": user.id, "guild": ctx.guild.id}):
                js = await db.durations.find_one({
                    "sub": user.id,
                    "domme": task["domme"],
                    "guild": ctx.guild.id,
                    "type": "task",
                    "task_id": task["task_id"]
                })

                if js and js["task_id"] == task["task_id"]:
                    full_dur = int(js["duration"])
                    t = format_timespan(full_dur)
                    results += f"\n**Task ID:** `{task['task_id']}`\n**Task:** `{task['task']}`\n**Time remaining:** `{t} remaining`"

            await msg.edit(content="", embed=Embed(
                title="Task list",
                description=f"**{user.mention}'s Tasks**\n{results}",
                color=int(c, 16)
            ))

        except Exception as e:
            print(e)
            await msg.edit(content="", embed=Embed(
                title="Error!",
                description="I have encountered an error!",
                color=int(c, 16)
            ))

    @task_comm.subcommand(
        name="completed",
        description="Mark a task as complete"
    )
    async def completed_task(self, ctx: Interaction, user: Member, task_id: int):
        opt = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not opt:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for BDSM. Ask the owner to use `/settings enable`.",
                color=0xffa4e4
            ), ephemeral=True)
            return

        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color["string"]
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else f"0x{c}"

        msg = await ctx.response.send_message("Running... please wait...")

        domme_roles = [r.id for r in ctx.user.roles]
        role_ids = [r.id for r in user.roles]

        try:
            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

            cont = False
            if result_domme["value"] in domme_roles or \
               result_ss["value"] in domme_roles or \
               result_s["value"] in domme_roles or \
               result_sd["value"] in domme_roles:
                cont = True

            if not cont:
                await msg.edit(content="", embed=Embed(title="Ew no.", description="**Stop bratting.**", color=int(c, 16)))
                return

            result = await db.task_list.find_one_and_delete({"sub": user.id, "domme": ctx.user.id, "guild": ctx.guild.id, "task_id": task_id})
            if not result:
                await msg.edit(content=f"{user.mention}", embed=Embed(title="Task ID not found", description=f"No task with ID `{task_id}`"))
                return

            duration_result = await db.durations.find_one_and_delete({"task_id": task_id, "domme": ctx.user.id, "sub": user.id})
            full_dur = int(duration_result["full_duration"] - duration_result["duration"])
            t = format_timespan(full_dur)

            await msg.edit(content=f"{user.mention}", embed=Embed(
                title="Task Completed!",
                description=f"**{user.mention} has completed their task!**",
                color=int(c, 16)
            ).add_field(name="Task ID:", value=f"```{task_id}```")
             .add_field(name="Task:", value=f"**{result['task']}**")
             .add_field(name="Time Taken:", value=f"{t}"))

        except Exception as e:
            print(e)
            await msg.edit(content="", embed=Embed(
                title="Error!",
                description="I have encountered an error!",
                color=int(c, 16)
            ))

    @task_comm.subcommand(
        name="give",
        description="Give your sub a task"
    )
    async def give_task(
        self,
        ctx: Interaction,
        user: Member,
        task: str,
        punishment: Literal["Gag", "Tie up", "Badword vowels", "DM", "Announce"],
        complete_by: str = "12h",
        task_id: int = None
    ):
        opt = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not opt:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for BDSM. Ask the owner to use `/settings enable`.",
                color=0xffa4e4
            ), ephemeral=True)
            return

        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color["string"]
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else f"0x{c}"

        msg = await ctx.response.send_message("Running... please wait...")
        domme_roles = [r.id for r in ctx.user.roles]
        role_ids = [r.id for r in user.roles]

        try:
            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

            cont = result_domme["value"] in domme_roles or \
                   result_ss["value"] in domme_roles or \
                   result_s["value"] in domme_roles or \
                   result_sd["value"] in domme_roles

            if not cont:
                await msg.edit(content="", embed=Embed(title="Ew no.", description="**Stop bratting.**", color=int(c, 16)))
                return

            task_id = random.randrange(1, 99999)
            existing = await db.task_list.find_one({"domme": ctx.user.id, "sub": user.id, "task_id": task_id, "guild": ctx.guild.id})
            while existing:
                task_id = random.randrange(1, 99999)
                existing = await db.task_list.find_one({"domme": ctx.user.id, "sub": user.id, "task_id": task_id, "guild": ctx.guild.id})

            try:
                duration = convert_to_seconds(complete_by)
            except Exception:
                duration = convert_to_seconds("12h")

            full_dur = int(duration)

            await db.durations.update_one(
                {"sub": user.id, "domme": ctx.user.id, "guild": ctx.guild.id, "type": "task", "task_id": task_id},
                {"$set": {"duration": full_dur, "full_duration": full_dur}},
                upsert=True
            )

            await db.task_list.update_one(
                {"sub": user.id, "domme": ctx.user.id, "guild": ctx.guild.id, "task_id": task_id},
                {"$set": {"task": task, "punishment": punishment, "channel": ctx.channel.id, "action": punishment}},
                upsert=True
            )

            t = format_timespan(full_dur)
            await msg.edit(content=f"{user.mention}", embed=Embed(
                title="New Task!",
                description=f"A new task has been added for {user.mention}",
                color=int(c, 16)
            ).add_field(name="Task ID:", value=f"```{task_id}```")
             .add_field(name="Task:", value=f"**{task}**")
             .add_field(name="Time given:", value=f"**{t}**"))

        except Exception as e:
            print(e)
            await msg.edit(content="", embed=Embed(
                title="Error!",
                description="I have encountered an error!",
                color=int(c, 16)
            ))
    @nextcord.slash_command(
        name="tie",
        description="Tie module",
        nsfw=True
    )
    async def tie(self, ctx: Interaction):
        pass

    @tie.subcommand(name="list", description="Use this command to see a list of tied up users.")
    async def tied(self, ctx: Interaction):
        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if options:
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                c = c.replace("#", "0x") if "#" in c else "0x" + c

            msg = await ctx.response.send_message("Running..Please wait..")
            results = ""
            num = 0

            async for result in db.tieup.find({"guild": ctx.guild.id}):
                num += 1
                user = await self.client.fetch_user(result["sub"])
                if user.discriminator == "0":
                    results += f"{num}: {user.name} ({user.id})\r\n"
                else:
                    results += f"{num}: {user.name}#{user.discriminator} ({user.id})\r\n"

            if not results:
                await msg.edit(content=None, embed=Embed(
                    title="There is no one tied up at this time!",
                    color=int(c, 16)
                ))
            else:
                await msg.edit(content=None, embed=Embed(
                    title="List of tied up subs",
                    description=results,
                    color=int(c, 16)
                ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`",
                color=0xffa4e4
            ), ephemeral=True)

    @tie.subcommand(
        name="bind",
        description="Bind a sub to a certain channel"
    )
    async def bind_tie(self, ctx: Interaction, user: Member = SlashOption(name="user", description="Sub to bind", required=True), channel: TextChannel = SlashOption(name="channel", description="Channel to bind to", required=False)):
        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if options:
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                c = c.replace("#", "0x") if "#" in c else "0x" + c

            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't tie up a bot!", color=int(c, 16)))
                return
            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    description="Really Trying to bind yourself? Desperate bitch",
                    color=int(c, 16)
                ))
                return

            domme_roles = [r.id for r in ctx.user.roles]
            role_ids = [r.id for r in user.roles]

            result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})

            if result_domme["value"] in domme_roles and result_domme["value"] in role_ids:
                await ctx.response.send_message(embed=Embed(description="Woah! You can't tie up a Domme!", color=int(c, 16)))
                return
            if result_domme["value"] in role_ids and result_s["value"] in domme_roles:
                await ctx.response.send_message(embed=Embed(description="Trying to brat are you? Loser!", color=int(c, 16)))
                return

            if any(result["value"] in domme_roles for result in [result_domme, result_s, result_sd, result_ss] if result):
                if not channel:
                    channel = ctx.channel
                existing = await db.tieup.find_one({"guild": ctx.guild.id, "sub": user.id})
                if existing:
                    await ctx.response.send_message(embed=Embed(description="This slut is already tied up!", color=int(c, 16)))
                    return

                await ctx.response.send_message(embed=Embed(
                    description=f"**{ctx.user.mention} binds {user.mention}'s to the floor so they know their place! They can now only type in {channel.mention}!**\r\n*Let's see them struggle!*",
                    color=int(c, 16)
                ))
                await db.tieup.update_one(
                    {"guild": ctx.guild.id, "domme": ctx.user.id, "sub": user.id},
                    {"$push": {"channel": channel.id}},
                    upsert=True
                )
            else:
                await ctx.response.send_message(embed=Embed(
                    description="You're too much of a loser to use this command",
                    color=int(c, 16)
                ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`",
                color=0xffa4e4
            ))

    @tie.subcommand(
        name="untie",
        description="Untie a sub"
    )
    async def untie(self, ctx: Interaction, user: Member = SlashOption(name="user", description="Sub to untie", required=True)):
        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if options:
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                c = c.replace("#", "0x") if "#" in c else "0x" + c

            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't untie a bot!", color=int(c, 16)))
                return
            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    description="Really Trying to untie yourself? Desperate bitch",
                    color=int(c, 16)
                ))
                return

            domme_roles = [r.id for r in ctx.user.roles]
            role_ids = [r.id for r in user.roles]

            result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})

            if result_domme["value"] in domme_roles and result_domme["value"] in role_ids:
                await ctx.response.send_message(embed=Embed(description="Woah! You can't untie a Domme!", color=int(c, 16)))
                return
            if result_domme["value"] in role_ids and result_s["value"] in domme_roles:
                await ctx.response.send_message(embed=Embed(description="Trying to brat are you? Loser!", color=int(c, 16)))
                return

            if any(result["value"] in domme_roles for result in [result_domme, result_s, result_sd, result_ss] if result):
                await ctx.response.send_message(embed=Embed(
                    description=f"**{ctx.user.mention} has decided to spare {user.mention}, so be thankful! You can now talk in other channels**",
                    color=int(c, 16)
                ))
                await db.tieup.delete_many({"guild": ctx.guild.id, "sub": user.id})
            else:
                await ctx.response.send_message(embed=Embed(
                    description="You're too much of a loser to use this command",
                    color=int(c, 16)
                ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="badword",
        description="Badword module",
        nsfw=True
    )
    async def badword(self, ctx: Interaction):
        pass

    # --------------------- LIST ---------------------
    @badword.subcommand(name="list", description="Use this command to see a list of users with badwords.")
    async def badworded(self, ctx: Interaction):
        if await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                if "#" not in c:
                    c = "0x" + c
                else:
                    c = c.replace("#", "0x")

            results = ""
            num = 0
            msg = await ctx.response.send_message("Running..Please wait...")

            async for result in db.badwords.find({"guild": ctx.guild.id}):
                num += 1
                user = await self.client.fetch_user(result["sub"])
                if user.discriminator == "0":
                    results += f"{num}: {user.name} ({user.id})\r\n"
                else:
                    results += f"{num}: {user.name}#{user.discriminator} ({user.id})\r\n"

            if not results:
                await msg.edit(content=None, embed=Embed(title="There is no one with badwords at this time!", color=int(c, 16)))
                return

            await msg.edit(content=None, embed=Embed(title="List of subs with badwords", description=results, color=int(c, 16)))

        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure the server using the `/settings enable` command",
                color=0xffa4e4
            ), ephemeral=True)

    # --------------------- ADD ---------------------
    @badword.subcommand(
        name="add",
        description="Add a badword to the sub's vocabulary"
    )
    async def add_badword(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="User to attach badword", required=True),
        word: str = SlashOption(name="word", description="Word to set to the sub's vocabulary", required=True)
    ):
        if await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                if "#" not in c:
                    c = "0x" + c
                else:
                    c = c.replace("#", "0x")

            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't add a badword to a bot!", color=int(c, 16)))
                return

            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    description="Woah you can't add a badword to yourself!",
                    color=int(c, 16)
                ))
                return

            domme_roles = [r.id for r in ctx.user.roles]
            role_ids = [r.id for r in user.roles]

            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

            if result_domme["value"] in domme_roles and result_domme["value"] in role_ids:
                await ctx.response.send_message(embed=Embed(description="Woah! You can't add a badword to a Domme!", color=int(c, 16)))
                return

            if result_domme["value"] in role_ids and result_s["value"] in domme_roles:
                await ctx.response.send_message(embed=Embed(description="Trying to brat are you? Loser!", color=int(c, 16)))
                return

            if any(result["value"] in domme_roles for result in [result_domme, result_s, result_sd, result_ss]):
                await db.badwords.update_one(
                    {"guild": ctx.guild.id, "sub": user.id},
                    {"$push": {"words": word.lower()}, "$set": {"domme": ctx.user.id}},
                    upsert=True
                )
                await ctx.response.send_message(embed=Embed(
                    description=f"**New badword added to {user.mention}'s vocabulary! They can no longer say `{word}`!**\n*Let's see them struggle!*",
                    color=int(c, 16)
                ))
                return

            await ctx.response.send_message(embed=Embed(
                description="This loser is trying to add a badword, I'm shaking my head in disbelief",
                color=int(c, 16)
            ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure the server using the `/settings enable` command",
                color=0xffa4e4
            ))

    # --------------------- REMOVE ---------------------
    @badword.subcommand(
        name="remove",
        description="Remove a badword from the sub's vocabulary"
    )
    async def badword_remove(
        self,
        ctx: Interaction,
        user: Member = SlashOption(description="Sub to remove the badword from", required=True),
        word: str = SlashOption(description="Word to remove from the badword list", required=True)
    ):
        if await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                if "#" not in c:
                    c = "0x" + c
                else:
                    c = c.replace("#", "0x")

            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't remove a badword from a bot!", color=int(c, 16)))
                return

            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    description="Woah you can't remove a badword from yourself!",
                    color=int(c, 16)
                ))
                return

            domme_roles = [r.id for r in ctx.user.roles]
            role_ids = [r.id for r in user.roles]

            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

            if any(result["value"] in domme_roles for result in [result_domme, result_s, result_sd, result_ss]):
                await db.badwords.update_one(
                    {"guild": ctx.guild.id, "sub": user.id},
                    {"$pull": {"words": word.lower()}},
                    upsert=True
                )
                await ctx.response.send_message(embed=Embed(
                    description=f"**Badword removed from {user.mention}'s vocabulary! They can now say `{word}`!**\n*Be thankful they're generous!*",
                    color=int(c, 16)
                ))
                return

            await ctx.response.send_message(embed=Embed(
                description="This loser is trying to add a badword, I'm shaking my head in disbelief",
                color=int(c, 16)
            ))

        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure the server using the `/settings enable` command",
                color=0xffa4e4
            ))

    # --------------------- CLEAR ---------------------
    @badword.subcommand(
        name="clear",
        description="Clear all badwords from a sub's vocabulary"
    )
    async def clear_badword(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="User to clear badwords for", required=True)
    ):
        if await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color["string"]
            if "0x" not in c:
                if "#" not in c:
                    c = "0x" + c
                else:
                    c = c.replace("#", "0x")

            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't clear badwords for a bot!", color=int(c, 16)))
                return

            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    description="Woah you can't clear badwords for yourself!",
                    color=int(c, 16)
                ))
                return

            domme_roles = [r.id for r in ctx.user.roles]
            role_ids = [r.id for r in user.roles]

            result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
            result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

            if any(result["value"] in domme_roles for result in [result_domme, result_s, result_sd, result_ss]):
                await db.badwords.delete_many({"guild": ctx.guild.id, "sub": user.id})
                await ctx.response.send_message(embed=Embed(
                    description=f"**All badwords have been cleared from {user.mention}**\n*Fun is over!*",
                    color=int(c, 16)
                ))
                return

            await ctx.response.send_message(embed=Embed(
                description="This loser is trying to clear a badword, I'm shaking my head in disbelief",
                color=int(c, 16)
            ))

        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM, please ask the owner to configure the server using the `/settings enable` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="prison",
        description="Prison function",
        nsfw=True
    )
    async def prison(self, ctx: Interaction):
        pass

    # -----------------------------
    # /prison lock
    # -----------------------------
    @prison.subcommand(
        name="lock",
        description="Lock a user in prison"
    )
    async def lock(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="User to lock in prison", required=True),
        opt: Literal["Praise me", "Degrade yourself", "Custom lines"] = SlashOption(name="option", description="Option for the message", required=True),
        lines: int = SlashOption(name="lines", required=True, description="Amount of lines to give"),
        message: str = SlashOption(name="message", description="Only use this if you're using custom lines", required=False)
    ):

        # BDSM config check
        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not options:
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`.",
                    color=0xffa4e4
                ),
                ephemeral=True
            )
            return

        color_doc = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color_doc.get('string', "#ff0000")
        if "0x" not in c:
            c = c.replace("#", "0x")

        msg = await ctx.response.send_message(embed=Embed(description=f"**Attempting to lock {user.mention} in prison..**"))
        bot = await ctx.guild.fetch_member(self.client.user.id)

        # Role hierarchy and safety checks
        if bot.top_role.position < user.top_role.position:
            await msg.edit(embed=Embed(title="You can't lock someone with a higher role than mine!", color=int(c, 16)))
            return
        if user.bot:
            await msg.edit(embed=Embed(title="You can't lock a bot!", color=int(c, 16)))
            return
        if user == ctx.user:
            await msg.edit(embed=Embed(description="Trying to lock yourself? Pathetic.", color=int(c, 16)))
            return

        # Check if already imprisoned
        if await db.prison.find_one({"sub": user.id, "guild": ctx.guild.id}):
            await msg.edit(embed=Embed(description=f"{user.mention} is already in prison!", color=int(c, 16)))
            return

        # Load configs
        result = await db.config.find_one({"key": "punishments", "guild": ctx.guild.id})
        channel_conf = await db.config.find_one({"guild": ctx.guild.id, "value": "punishments"})
        if not result or not channel_conf:
            await msg.edit(embed=Embed(title="This server is missing punishment configuration.", color=int(c, 16)))
            return

        a_channel = self.client.get_channel(channel_conf['channel'])
        username = ctx.user.nick or ctx.user.name

        # Async load lines file
        async with aiofiles.open("CONF/lines.json", mode="r") as f:
            load_json = json.loads(await f.read())

        choice = ""
        if opt == "Praise me":
            choice = random.choice(load_json['praise'])
        elif opt == "Degrade yourself":
            choice = random.choice(load_json['degrade'])
        elif opt == "Custom lines":
            choice = message or "..."

        if "%username%" in choice:
            choice = choice.replace("%username%", username)

        # Stylize message
        words = "".join(
            letter.upper() if random.choice([True, False]) else letter.lower()
            for letter in choice
        )
        if random.choice([True, False]):
            words += "."

        choice = unicodedata.normalize("NFKD", words).encode("ascii", "ignore").decode("utf-8")

        # Write to temp files asynchronously
        async with aiofiles.open(f"{ctx.guild.id}{user.id}.txt", "w") as f:
            await f.write(choice)

        # Run text formatting command asynchronously
        async def run_cmd(cmd):
            proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            await proc.communicate()

        await run_cmd(f"fmt {ctx.guild.id}{user.id}.txt > fmt_{ctx.guild.id}{user.id}.txt")
        await run_cmd(f"pango-view --font=\"Ldfcomicsans\" --dpi=120 -qo {ctx.guild.id}{user.id}.png fmt_{ctx.guild.id}{user.id}.txt")

        await db.prison.update_one(
            {"guild": ctx.guild.id, "sub": user.id},
            {"$set": {"domme": ctx.user.id, "words": choice, "lines": lines}},
            upsert=True
        )

        # Restrict all other channels
        for all_channels in ctx.guild.channels:
            if int(all_channels.id) == int(channel_conf['channel']):
                continue
            if all_channels.permissions_for(user).send_messages:
                overwrites = all_channels.overwrites_for(user)
                overwrites.view_channel = False
                overwrites.send_messages = False
                await all_channels.set_permissions(user, overwrite=overwrites)
                await db.prison_channels.update_one(
                    {"user": user.id, "guild": ctx.guild.id},
                    {"$push": {"channels": all_channels.id}},
                    upsert=True
                )

        # Assign prison role
        role = ctx.guild.get_role(result['value'])
        if role:
            await user.add_roles(role)

        # Send prison image
        async with aiofiles.open(f"{ctx.guild.id}{user.id}.png", "rb") as f:
            file = File(f.name, filename="prison.png")
        await a_channel.send(
            f"{user.mention}, You have been locked in prison! You must write the following lines `{lines}` time(s) ||(Auto unlocking in 4 hours)||",
            file=file
        )

        await msg.edit(content=None, embed=Embed(description=f"{user.mention} has been locked in prison.", color=int(c, 16)))

        await db.durations.update_one(
            {"sub": user.id, "domme": ctx.user.id, "guild": ctx.guild.id, "type": "prison"},
            {"$set": {"duration": 14400, "full_duration": 14400}},
            upsert=True
        )

    # -----------------------------
    # /prison unlock
    # -----------------------------
    @prison.subcommand(
        name="unlock",
        description="Unlock a user from prison"
    )
    async def unlock(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="User to unlock", required=True)
    ):

        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not options:
            await ctx.response.send_message(embed=Embed(title="Not configured!", description="This server is not configured for BDSM.", color=0xffa4e4))
            return

        color_doc = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color_doc.get('string', "#ff0000")
        if "0x" not in c:
            c = c.replace("#", "0x")

        msg = await ctx.response.send_message(embed=Embed(description=f"**Attempting to unlock {user.mention} from prison..**"))

        # Validation
        if user.bot:
            await msg.edit(embed=Embed(title="You can't release a bot!", color=int(c, 16)))
            return
        if user == ctx.user:
            await msg.edit(embed=Embed(description="Why would you unlock yourself?", color=int(c, 16)))
            return

        prison_doc = await db.prison.find_one({"sub": user.id, "guild": ctx.guild.id})
        if not prison_doc:
            await msg.edit(embed=Embed(description=f"{user.mention} isn't in prison!", color=int(c, 16)))
            return

        result = await db.config.find_one({"key": "punishments", "guild": ctx.guild.id})
        if not result:
            await msg.edit(embed=Embed(title="Missing configuration.", color=int(c, 16)))
            return

        await msg.edit(embed=Embed(description=f"Releasing {user.mention}... Please wait.", color=int(c, 16)))

        # Restore channel permissions
        channel_list = await db.prison_channels.find_one({"guild": ctx.guild.id, "user": user.id})
        if channel_list and isinstance(channel_list.get("channels"), list):
            for ch in channel_list["channels"]:
                channel = self.client.get_channel(ch)
                if channel:
                    await channel.set_permissions(user, overwrite=None)

        # Remove prison role
        role = ctx.guild.get_role(result['value'])
        if role:
            await user.remove_roles(role)

        # Clean up database
        await db.prison.delete_many({"sub": user.id, "guild": ctx.guild.id})
        await db.prison_channels.delete_many({"guild": ctx.guild.id, "user": user.id})
        await db.durations.delete_many({"sub": user.id, "guild": ctx.guild.id, "type": "prison"})

        # Async file deletion
        for path in [
            f"{ctx.guild.id}{user.id}.png",
            f"{ctx.guild.id}{user.id}.txt",
            f"fmt_{ctx.guild.id}{user.id}.txt"
        ]:
            try:
                await asyncio.to_thread(os.remove, path)
            except FileNotFoundError:
                continue

        await msg.edit(content=None, embed=Embed(description=f"{user.mention} has been released from prison.", color=int(c, 16)))

    @nextcord.slash_command(
        name="gag",
        description="Gag someone with a specified gag.",
        nsfw=True
    )
    async def gag_command(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="Sub to gag", required=True),
        gag_type: Literal[
            "kitty gag", "puppy gag", "cow gag", "piggy gag",
            "ball gag", "cutesy gag", "reverse gag", "mangle gag", "ungag"
        ] = SlashOption(name="gag", description="Type of gag to place in sub's mouth", required=True),
        duration: str = SlashOption(name="duration", description="Duration (default: 20m)", required=False),
        force: bool = SlashOption(name="force", description="Forcefully gag?", required=False),
        channel: TextChannel = SlashOption(name="channel", description="Channel for webhook", required=False),
        delete_messages: bool = SlashOption(name="delete_messages", description="Delete sub's messages?", default=False, required=False)
    ):

        # Verify BDSM config
        options = await db.options.find_one({"guild": ctx.guild.id, "bdsm": True})
        if not options:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Please use `/settings enable` first.",
                color=0xffa4e4
            ))
            return

        color_doc = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color_doc['string']
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else "0x" + c

        # Validation checks
        if user == self.client.user:
            await ctx.response.send_message(embed=Embed(description="Why are you trying to gag me? Don't touch me!", color=int(c, 16)))
            return
        if user.bot:
            await ctx.response.send_message(embed=Embed(title="You can't gag a bot!", color=int(c, 16)))
            return
        if user == ctx.user:
            await ctx.response.send_message(embed=Embed(description="Trying to gag yourself? Pathetic.", color=int(c, 16)))
            return

        # Role logic
        domme_roles = [r.id for r in ctx.user.roles]
        sub_roles = [r.id for r in user.roles]
        result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        result_domme = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
        result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})

        # Role hierarchy enforcement
        if result_d and result_d["value"] in domme_roles:
            await ctx.response.send_message(embed=Embed(description="You really thought that was going to work? Loser.", color=int(c, 16)))
            return
        if result_s:
            if result_s["value"] in domme_roles and result_domme["value"] in sub_roles:
                await ctx.response.send_message(embed=Embed(description="Trying to brat are you? Pathetic.", color=int(c, 16)))
                return
        if result_domme and result_domme["value"] in domme_roles and result_domme["value"] in sub_roles:
            await ctx.response.send_message(embed=Embed(description="Woah! You can't gag another domme!", color=int(c, 16)))
            return
        if result_domme and result_domme["value"] in sub_roles and result_domme["value"] not in domme_roles:
            await ctx.response.send_message(embed=Embed(description="Trying to brat are you? You're so pathetic.", color=int(c, 16)))
            return

        if not any([
            result_domme and result_domme["value"] in domme_roles,
            result_sd and result_sd["value"] in domme_roles,
            result_ss and result_ss["value"] in domme_roles,
            result_s and result_s["value"] in domme_roles
        ]):
            await ctx.response.send_message(embed=Embed(description="You really thought that was going to work? Loser.", color=int(c, 16)))
            return

        # Duration parsing
        try:
            seconds = convert_to_seconds(duration or "20m")
        except ValueError:
            await ctx.response.send_message(embed=Embed(
                title="Syntax Error!",
                description=f"{duration} is not valid! Try formats like `10m`, `2h`, `1d`, `1w`.",
                color=int(c, 16)
            ))
            return

        # Determine gag type response
        command_str, words, emoji = "", None, None
        if gag_type == "reverse gag":
            command_str = f"The divine {ctx.user.mention} has decided to gag you — all messages will be reversed!"
            words = []
        elif gag_type == "mangle gag":
            command_str = f"The divine {ctx.user.mention} has decided to gag you — parts of your text will be hidden!"
            words = []
        elif gag_type == "cutesy gag":
            command_str = f"The divine {ctx.user.mention} has decided to gag you — you’re so cute now!~"
            words = []
        elif gag_type == "kitty gag":
            emoji = "🐱"
            command_str = f"The divine {ctx.user.mention} has {'forcefully ' if force else ''}decided to gag you — purr like a good kitty!~"
            words = ["mrowww", "meoww", "purrrrr", "purrrr~"]
        elif gag_type == "puppy gag":
            emoji = "🐶"
            command_str = f"The divine {ctx.user.mention} has {'forcefully ' if force else ''}decided to gag you — bark like a good puppy!~"
            words = ["rrrruff", "bark", "mmmph", "woofff", "rrrruff~"]
        elif gag_type == "piggy gag":
            emoji = "🐷"
            command_str = f"The divine {ctx.user.mention} has {'forcefully ' if force else ''}decided to gag you — oink like a good piggy!~"
            words = ["oink", "snort"]
        elif gag_type == "cow gag":
            emoji = "🐮"
            command_str = f"The divine {ctx.user.mention} has {'forcefully ' if force else ''}decided to gag you — moo like a good cow!~"
            words = ["mroooo", "mooooo", "mroooo~"]
        elif gag_type == "ball gag":
            emoji = "🔴"
            command_str = f"The divine {ctx.user.mention} has {'forcefully ' if force else ''}decided to gag you with a ball gag — you can’t speak clearly!~"
            words = ["mmmmmf", "mmmmph", "mmph", "mmmmphh", "mmmmf", "mphhh~"]
        elif gag_type == "ungag":
            existing = await db.gagged.find_one({"guild": ctx.guild.id, "sub": user.id})
            if not existing:
                await ctx.response.send_message(embed=Embed(description=f"{user.mention} is not gagged by anyone.", color=int(c, 16)))
                return
            await db.gagged.delete_one({"guild": ctx.guild.id, "sub": user.id})
            await db.durations.delete_many({"sub": user.id, "guild": ctx.guild.id, "type": "gag"})
            async with aiohttp.ClientSession() as session:
                for wh in existing.get("webhooks", []):
                    try:
                        webhook = Webhook.from_url(wh, session=session)
                        await webhook.delete()
                    except Exception:
                        continue
            await ctx.response.send_message(embed=Embed(description=f"**{user.mention} can now move their mouth again...**", color=int(c, 16)))
            return

        # Handle gag application
        username = user.nick or user.name
        embed = Embed(description=f"**{command_str}**", color=int(c, 16))
        gag_image = await db.custom.find_one({"guild": ctx.guild.id, "type": "gag_image"})
        images_enabled = await db.options.find_one({"images": True, "guild": ctx.guild.id})
        if images_enabled and gag_image:
            embed.set_image(url=gag_image["string"])

        target_channel = channel or ctx.channel
        avatar = user.display_avatar.url if user.display_avatar else user.default_avatar.url

        # Delete old webhooks if re-gagging
        old_gag = await db.gagged.find_one({"sub": user.id, "guild": ctx.guild.id})
        if old_gag:
            async with aiohttp.ClientSession() as session:
                for wh in old_gag.get("webhooks", []):
                    try:
                        webhook = Webhook.from_url(wh, session=session)
                        await webhook.delete()
                    except Exception:
                        pass
            await db.gagged.delete_one({"sub": user.id, "guild": ctx.guild.id})

        # Send response and create new webhook
        await ctx.response.send_message(content=f"{user.mention}", embed=embed)
        wh = await target_channel.create_webhook(name=username, avatar=await user.display_avatar.read())
        await db.gagged.update_one(
            {"guild": ctx.guild.id, "sub": user.id},
            {"$set": {
                "webhooks": [wh.url],
                "domme": ctx.user.id,
                "words": words,
                "gag_type": gag_type,
                "delete": delete_messages
            }},
            upsert=True
        )
        await db.durations.update_one(
            {"sub": user.id, "domme": ctx.user.id, "guild": ctx.guild.id, "type": "gag"},
            {"$set": {"duration": seconds, "full_duration": seconds}},
            upsert=True
        )
    @nextcord.slash_command(
        name="status",
        description="Check the status of ownership",
        nsfw=True
    )
    async def status(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to check", required=False)):
        if not user:
            user = ctx.user
        if await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c="0x"+c
                else:
                    arr = c.split("#")
                    c = "0x"+arr[1]
            print (c)
            if user == self.client.user:
                userame = ""
                if not user.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{user.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                else:
                    username = user.nick
                await ctx.response.send_message(embed=Embed(title="I'm a free bird!", color=int(c, 16)).set_author(name=f"{username}").set_thumbnail(url=self.client.user.display_avatar.url))
                return
            if not user:
                user = ctx.user
            if user.bot:
                await ctx.response.send_message(embed=Embed(title="You can't get ownership status of a bot!", color=int(c, 16)))
                return
            msg = await ctx.response.send_message("Running..Please wait...")
            role_ids = []
            curr = [role_ids.append(role.id) for role in user.roles]
            try:
                embed = None
                result_d = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
                result_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
                result_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
                result_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
                result_sub = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
                embed = None
                username = ""
                string = ""
                if result_d['value'] in role_ids:
                    string = ""
                    claim = await db.claims.find_one({"guild": ctx.guild.id, "domme": user.id})
                    if len(claim['submissives']) != 0:
                        string += "\r\n**My subbies**"
                        for cl in claim['submissives']:
                            string += f"\r\n* <@{cl}>\r\n"
                    else:
                        string += f"\r\n**I don't have any subbies currently!**"
                    username = ""
                    if not user.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{user.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = user.nick
                    embed = Embed(description=string, color=int(c, 16)).set_thumbnail(user.display_avatar.url).set_author(name=f"{username}")
                if result_s:
                    duration = None
                    duration = await db.durations.find_one({"sub": user.id, "guild": ctx.guild.id, "type": "gag"})

                    if not duration:
                        duration = "No duration has been set"
                    else:
                        try:
                            temp_duration = duration.get("duration", "No duration has been set")
                            duration = f"{format_timespan(temp_duration)} remaining"
                        except KeyError:
                            duration = "No duration has been set."
                    if result_s['value'] in role_ids or result_sd['value'] in role_ids or result_ss['value'] in role_ids:
                        sub_get = await db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
                        string = """
                        
        """
                        restrictions = """

"""
                        pris = await db.prison.find_one({"sub": user.id, "guild": ctx.guild.id})
                        if pris:
                            restrictions += f"""**Imprisonment:** ``Yes``
**Domme:** <@{pris['domme']}>
**Lines Left:** ``{pris['lines']} lines``

"""
                        else:
                            restrictions += """**Imprisonment:** ``No``

"""
                        gag = await db.gagged.find_one({"sub": user.id, "guild": ctx.guild.id})
                        if gag:
                            restrictions += f"""**Gagged:** ``Yes``
**Domme:** <@{gag['domme']}>
**Gag Type:** ``{gag['gag_type']}``
**Duration:** ``{duration}``

"""
                        else:
                            restrictions += """**Gagged:** ``No``

"""
                        blind = await db.chans.find_one({"sub": user.id, "guild": ctx.guild.id})
                        if blind:
                            restrictions += f"""**Blindfolded:** ``Yes``
**Domme:** <@{blind['domme']}>
**Text Channel:** <#{blind['text_channel']}>
**Voice Channel:** <#{blind['voice_channel']}>

"""
                        else:
                            restrictions += """**Blindfolded:** ``No``

"""
                        tied = await db.tieup.find_one({"sub": user.id, "guild": ctx.guild.id})
                        if tied:
                            chans = ""
                            for chan in tied['channel']:
                                chans += f"\r\n* <#{chan}>\r\n"
                            restrictions += f"""**Tied up:** ``Yes``
**Domme:** <@{tied['domme']}>
**Channels:** {chans}

"""
                        else:
                            restrictions += """**Tied up:** ``No``

"""
                        badword = await db.badwords.find_one({"sub": user.id, "guild": ctx.guild.id})
                        if badword:
                            words = ""
                            for word in badword['words']:
                                words += f"\r\n* {word}\r\n"
                            restrictions += f"""**Has Badwords:** ``Yes``
**Domme:** <@{badword['domme']}>
**Words restricted:** {words}

"""
                        else:
                            restrictions += """**Has badwords:** ``No``

"""
                        if sub_get:
                                if sub_get['domme']:
                                    string += f"\r\n**<@{sub_get['domme']}> owns me and I am thrilled to be their naughty little slut.**\r\n"
                                else:
                                    string += f"**Nobody owns me, i'm sad :c**"
                        else:
                                string += f"**Nobody owns me, i'm sad :c**"

                        domme_get = await db.claims.find_one({"guild": ctx.guild.id, "domme": user.id})
                        if len(domme_get['submissives']) != 0:
                            string += f"\r\n**My subbies**\r\n"
                            for claim in domme_get['submissives']:
                                    string += f"* <@{claim}>\r\n"
                        else:
                            string += "\r\n**I have no subbies currently!**\r\n"
                        string += restrictions
                        print (string)
                        username = ""
                        if not user.nick:
                            req = requests.get(f"https://discord.com/api/v10/users/{user.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                            js = json.loads(req.text)
                            username = js['global_name']
                        else:
                            username = user.nick
                            
                        embed = Embed(description=string, color=int(c, 16)).set_thumbnail(user.display_avatar.url).set_author(name=f"{username}")

                if result_sub['value'] in role_ids:
                    claim = await db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
                    string = ""
                    restrictions = """

"""
                    pris = await db.prison.find_one({"sub": user.id, "guild": ctx.guild.id})
                    if pris:
                            restrictions += f"""**Imprisonment:** ``Yes``
**Domme:** <@{pris['domme']}>
**Lines Left:** ``{pris['lines']} lines``

"""
                    else:
                            restrictions += """**Imprisonment:** ``No``

"""
                    gag = await db.gagged.find_one({"sub": user.id, "guild": ctx.guild.id})
                    if gag:
                            restrictions += f"""**Gagged:** ``Yes``
**Domme:** <@{gag['domme']}>
**Gag Type:** ``{gag['gag_type']}``
**Duration:** ``{duration}``

"""
                    else:
                            restrictions += """**Gagged:** ``No``

"""
                    blind = await db.chans.find_one({"sub": user.id, "guild": ctx.guild.id})
                    if blind:
                            restrictions += f"""**Blindfolded:** ``Yes``
**Domme:** <@{blind['domme']}>
**Text Channel:** <#{blind['text_channel']}>
**Voice Channel:** <#{blind['voice_channel']}>

"""
                    else:
                            restrictions += """**Blindfolded:** ``No``

"""
                    tied = await db.tieup.find_one({"sub": user.id, "guild": ctx.guild.id})
                    if tied:
                            chans = ""
                            for chan in tied['channel']:
                                chans += f"\r\n* <#{chan}>\r\n"
                            restrictions += f"""**Tied up:** ``Yes``
**Domme:** <@{tied['domme']}>
**Channels:** {chans}

"""
                    else:
                            restrictions += """**Tied up:** ``No``

"""
                    badword = await db.badwords.find_one({"sub": user.id, "guild": ctx.guild.id})
                    if badword:
                        words = ""
                        for word in badword['words']:
                                words += f"\r\n* {word}\r\n"
                        restrictions += f"""**Has Badwords:** ``Yes``
**Domme:** <@{badword['domme']}>
**Words restricted:** {words}

"""
                    else:
                            restrictions += """**Has badwords:** ``No``

"""
                    if claim:
                        string += f"\r\n**<@{claim['domme']}> owns me and I am thrilled to be their naughty little slut.**"
                        #get_tie_results = await db.gagged.
                        
                    else:
                        string += "**\r\nNobody owns me, i'm sad :c**"
                    username = ""
                    if not user.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{user.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = user.nick
                    string += restrictions
                    embed = Embed(color=int(c, 16),description=string).set_thumbnail(user.display_avatar.url).set_author(name=f"{username}")
                    file = File("status.jpg", filename="status.jpg")
                    x = await db.custom.find_one({"guild": ctx.guild.id, "type": "status_image"})
                    y = await db.options.find_one({"guild": ctx.guild.id, "images": True})
                    if y:
                        print(x['string'])
                        embed.set_image(f"{x['string']}")
                await msg.edit(content="", embed=embed)
            except Exception as fe:
                print (fe)
                await msg.edit("Fetching failed! This server is not configured.")
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for BDSM, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    async def fetch_username(self, user_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://discord.com/api/v10/users/{user_id}",
                headers={"Authorization": f"Bot {os.getenv('TOKEN')}"}
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("global_name", "Unknown")
                return "Unknown"

    async def get_color(self, guild_id):
        color_data = await db.custom.find_one({"type": "color", "guild": guild_id})
        c = color_data.get("string", "0xffa4e4") if color_data else "0xffa4e4"
        if "0x" not in c:
            c = "0x" + c.replace("#", "")
        return int(c, 16)

    # -----------------------------
    # /gagged command
    # -----------------------------
    @nextcord.slash_command(name="gagged", description="See a list of gagged users.", nsfw=True)
    async def gagged(self, ctx: Interaction):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`.",
                    color=0xffa4e4
                ), ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)
        results = ""
        num = 0
        msg = await ctx.response.send_message("Running.. Please wait..")

        async for result in db.gagged.find({"guild": ctx.guild.id}):
            num += 1
            user = await self.client.fetch_user(result['sub'])
            if user.discriminator == "0":
                results += f"{num}: {user.name} ({user.id})\r\n"
            else:
                results += f"{num}: {user.name}#{user.discriminator} ({user.id})\r\n"

        if num == 0:
            await msg.edit(embed=Embed(title="There is no one gagged at this time!", color=c))
        else:
            await msg.edit(embed=Embed(title="List of gagged subs", description=results, color=c))

    # -----------------------------
    # /locked command
    # -----------------------------
    @nextcord.slash_command(name="locked", description="See a list of locked users.", nsfw=True)
    async def locked(self, ctx: Interaction):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`.",
                    color=0xffa4e4
                ), ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)
        results = ""
        num = 0
        msg = await ctx.response.send_message("Running.. Please wait..")

        async for result in db.prison.find({"guild": ctx.guild.id}):
            num += 1
            user = await self.client.fetch_user(result['sub'])
            if user.discriminator == "0":
                results += f"{num}: {user.name} ({user.id})\r\n"
            else:
                results += f"{num}: {user.name}#{user.discriminator} ({user.id})\r\n"

        if num == 0:
            await msg.edit(embed=Embed(title="There is no one locked at this time!", color=c))
        else:
            await msg.edit(embed=Embed(title="List of locked subs", description=results, color=c))

    # -----------------------------
    # /say command
    # -----------------------------
    @nextcord.slash_command(name="say", description="Say a message as one of your subs.", nsfw=True)
    async def say(
        self,
        ctx: Interaction,
        user: Member = SlashOption(name="user", description="Sub to say something as.", required=True),
        message: str = SlashOption(name="message", description="Message to say.", required=True),
        channel: TextChannel = SlashOption(name="channel", description="Channel to redirect the message to", required=False)
    ):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`.",
                    color=0xffa4e4
                ), ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)
        config = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        if not config:
            await ctx.response.send_message(
                embed=Embed(title="Server not configured correctly!", color=c, description="Please ask an administrator to configure it!"),
                ephemeral=True
            )
            return

        # Block self & bot
        if self.client.user.id == user.id:
            await ctx.response.send_message(embed=Embed(description="Don't you dare touch me, I'm a free bird!"), ephemeral=True)
            return
        if user.id == ctx.user.id:
            await ctx.response.send_message(embed=Embed(title="Uh...", description="You're trying to force words as yourself...How desperate are you?", color=c), ephemeral=True)
            return

        # Check ownership
        domme_claim = await db.claims.find_one({"guild": ctx.guild.id, "domme": ctx.user.id, "submissives": {"$in": [user.id]}})
        if not domme_claim:
            await ctx.response.send_message(embed=Embed(description="You do not own this person.", color=c), ephemeral=True)
            return

        msg = await ctx.response.send_message("Running.. Please wait..", ephemeral=True)
        username = user.nick or await self.fetch_username(user.id)
        channel = channel or ctx.channel

        avatar = user.display_avatar.url if user.display_avatar else None
        webhook = await channel.create_webhook(name=username, avatar=await avatar.read() if avatar else None)
        await webhook.send(message)
        await webhook.delete()
        await msg.edit(content="", embed=Embed(description=f"Your message has been sent as {user.mention}", color=c))
    @nextcord.slash_command(name="blindfold", description="Blindfold module", nsfw=True)
    async def blindfold(self, ctx: Interaction):
        pass

    # -----------------------------
    # Blindfold Add Subcommands
    # -----------------------------
    @blindfold.subcommand(name="add", description="Add module")
    async def add_blindfold(self, ctx: Interaction):
        pass

    @add_blindfold.subcommand(name="member", description="Add a sub to blindfold")
    async def sub_add(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to blindfold", required=True)):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM, please ask the owner to configure it using `/settings enable`.",
                    color=0xffa4e4
                ), ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)

        config = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        if not config:
            await ctx.response.send_message(embed=Embed(title="Server not configured!", color=c, description="Please ask an admin to configure it!"))
            return

        # Prevent self or bot blindfold
        if user.id == self.client.user.id:
            await ctx.response.send_message(embed=Embed(description="Don't you dare touch me, I'm a free bird!"))
            return
        if user.id == ctx.user.id:
            await ctx.response.send_message(embed=Embed(title="Uh...", description="You're trying to blindfold yourself...How desperate are you?", color=c))
            return

        # Roles
        role_ids = [r.id for r in user.roles]
        domme_roles = [r.id for r in ctx.user.roles]

        if config['value'] in domme_roles:
            await ctx.response.send_message(embed=Embed(title="Ew no.", description="Ew. Stop trying to brat, it's not cute.", color=c))
            return

        # Already blindfolded?
        if await db.chans.find_one({"guild": ctx.guild.id, "sub": user.id}):
            await ctx.response.send_message(embed=Embed(description="The person is already blindfolded!", color=c))
            return

        # Domme permission check
        config_d = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        config_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

        if config_d['value'] in role_ids:
            await ctx.response.send_message(embed=Embed(description="The person is a Domme, not a sub.", color=c))
            return

        msg = await ctx.response.send_message("Blindfolding..Please wait..")

        username = user.nick or await self.fetch_username(user.id)

        # Hide existing channels
        for ch in ctx.guild.channels:
            if ch.permissions_for(user).view_channel:
                overwrites = ch.overwrites_for(user)
                overwrites.view_channel = False
                await ch.set_permissions(user, overwrite=overwrites, reason="blindfold")
                await db.channels.update_one({"user": user.id, "guild": ctx.guild.id}, {"$push": {"channels": ch.id}}, upsert=True)

        # Create text and voice channels
        text_channel = await ctx.guild.create_text_channel(name=f"text-punishment-{username}", nsfw=True)
        voice_channel = await ctx.guild.create_voice_channel(name=f"voice-punishment-{username}")

        # Set permissions
        sub_perms = nextcord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            embed_links=True,
            add_reactions=True,
            use_external_emojis=True,
            use_slash_commands=True,
            read_messages=True,
            read_message_history=True,
            connect=True,
            speak=True,
            stream=True,
            use_voice_activation=True
        )
        domme_perms = nextcord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            embed_links=True,
            add_reactions=True,
            use_external_emojis=True,
            use_slash_commands=True,
            read_messages=True,
            read_message_history=True,
            connect=True,
            speak=True,
            stream=True,
            use_voice_activation=True,
            mute_members=True,
            deafen_members=True
        )

        await text_channel.set_permissions(user, overwrite=sub_perms)
        await text_channel.set_permissions(ctx.user, overwrite=domme_perms)
        await voice_channel.set_permissions(user, overwrite=sub_perms)
        await voice_channel.set_permissions(ctx.user, overwrite=domme_perms)

        # Save to DB
        await db.chans.update_one(
            {"guild": ctx.guild.id, "sub": user.id, "domme": ctx.user.id},
            {"$set": {"text_channel": text_channel.id, "voice_channel": voice_channel.id}},
            upsert=True
        )

        await msg.edit(content="", embed=Embed(description=f"{user.mention} is now blindfolded. Let the fun begin!", color=c))

    # -----------------------------
    # Blindfold Remove Subcommands
    # -----------------------------
    @blindfold.subcommand(name="remove", description="Remove a blindfold")
    async def remove_blindfold(self, ctx: Interaction):
        pass

    @remove_blindfold.subcommand(name="member", description="Remove a sub from a blindfold")
    async def remove_member_blind(self, ctx: Interaction, user: Member = SlashOption(name="user", description="Submissive to remove the blindfold from")):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(embed=Embed(title="Not configured!", description="This server is not configured for BDSM.", color=0xffa4e4), ephemeral=True)
            return

        c = await self.get_color(ctx.guild.id)
        res = await db.chans.find_one({"guild": ctx.guild.id, "sub": user.id, "domme": ctx.user.id})
        if not res:
            await ctx.response.send_message(embed=Embed(description="This sub is not blindfolded!", color=c))
            return

        msg = await ctx.response.send_message("Removing blindfold.. Please wait..")

        # Restore channels permissions
        channels_data = await db.channels.find_one({"guild": ctx.guild.id, "user": user.id})
        if channels_data and "channels" in channels_data:
            if isinstance(channels_data["channels"], list):
                for ch_id in channels_data["channels"]:
                    channel = self.client.get_channel(ch_id)
                    await channel.set_permissions(user, overwrite=None)
            await db.channels.delete_many({"guild": ctx.guild.id, "user": user.id})

        # Delete punishment channels
        text_channel = self.client.get_channel(res['text_channel'])
        voice_channel = self.client.get_channel(res['voice_channel'])
        if text_channel:
            await text_channel.delete()
        if voice_channel:
            await voice_channel.delete()

        await db.chans.delete_many({"guild": ctx.guild.id, "sub": user.id, "domme": ctx.user.id})

        await msg.edit(content="", embed=Embed(description=f"{user.mention} has now been removed of their blindfold", color=c))
    # -----------------------------
    # Blindfold Add Spectator
    # -----------------------------
    @add_blindfold.subcommand(name="spectator", description="Add a spectator")
    async def spectator_add(self, ctx: Interaction, user: Member = SlashOption(name="spectator", description="Spectator to add", required=True), sub: Member = SlashOption(name="sub", description="Sub to watch", required=True)):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM. Please ask the owner to configure using `/settings enable`.",
                    color=0xffa4e4
                ),
                ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)

        # Prevent bot spectator
        if user.id == self.client.user.id:
            await ctx.response.send_message(embed=Embed(description="I'm already watching silly."))
            return

        res = await db.chans.find_one({"guild": ctx.guild.id, "sub": sub.id, "domme": ctx.user.id})
        if not res:
            await ctx.response.send_message(embed=Embed(description="The sub is not currently blindfolded!", color=c))
            return

        text_channel = self.client.get_channel(res['text_channel'])
        voice_channel = self.client.get_channel(res['voice_channel'])

        # Permissions for spectator
        perms = nextcord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            embed_links=True,
            add_reactions=True,
            use_external_emojis=True,
            use_slash_commands=True,
            read_messages=True,
            read_message_history=True,
            connect=True,
            speak=True,
            stream=True,
            use_voice_activation=True,
            mute_members=True,
            deafen_members=True
        )

        await text_channel.set_permissions(user, overwrite=perms)
        await voice_channel.set_permissions(user, overwrite=perms)

        await text_channel.send(embed=Embed(description=f"Please welcome {user.mention} to get front row seats!", color=c))
        await ctx.response.send_message(embed=Embed(description=f"{user.mention} has been added as a spectator for {sub.mention}", color=c))


    # -----------------------------
    # Blindfold Remove Spectator
    # -----------------------------
    @remove_blindfold.subcommand(name="spectator", description="Remove a spectator")
    async def spectator_remove(self, ctx: Interaction, user: Member = SlashOption(name="spectator", description="Spectator to remove", required=True), sub: Member = SlashOption(name="sub", description="Sub being watched", required=True)):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(
                embed=Embed(
                    title="Not configured!",
                    description="This server is not configured for BDSM. Please ask the owner to configure using `/settings enable`.",
                    color=0xffa4e4
                ),
                ephemeral=True
            )
            return

        c = await self.get_color(ctx.guild.id)

        if user.id == self.client.user.id:
            await ctx.response.send_message(embed=Embed(description="I'm already watching silly."))
            return

        res = await db.chans.find_one({"guild": ctx.guild.id, "sub": sub.id, "domme": ctx.user.id})
        if not res:
            await ctx.response.send_message(embed=Embed(description="The sub is not currently blindfolded!", color=c))
            return

        # Remove spectator permissions
        text_channel = self.client.get_channel(res['text_channel'])
        voice_channel = self.client.get_channel(res['voice_channel'])

        perms = nextcord.PermissionOverwrite(
            view_channel=False,
            send_messages=False,
            attach_files=False,
            embed_links=False,
            add_reactions=False,
            use_external_emojis=False,
            use_slash_commands=False,
            read_messages=False,
            read_message_history=False,
            connect=False,
            speak=False,
            stream=False,
            use_voice_activation=False,
            mute_members=False,
            deafen_members=False
        )

        await text_channel.set_permissions(user, overwrite=perms)
        await voice_channel.set_permissions(user, overwrite=perms)

        await ctx.response.send_message(embed=Embed(description=f"{user.mention} has been removed from the spectators of {sub.mention}", color=c))
    @nextcord.slash_command(
    name="own",
    description="Own a sub",
    nsfw=True
    )
    async def own(self, ctx: Interaction, user: Member = SlashOption(name="user", description="Sub to own", required=True)):
        # Check if server is configured
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Please ask the owner to configure using `/settings enable`.",
                color=0xffa4e4
            ), ephemeral=True)
            return

        # Get server color
        color_doc = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color_doc['string']
        if "0x" not in c:
            c = "0x"+c.replace("#", "0x") if "#" in c else "0x"+c

        # Get config
        config = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        config_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_d = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        config_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})
        max_subs = await db.config.find_one({"guild": ctx.guild.id, "key": "max subs"})

        if not config:
            await ctx.response.send_message(embed=Embed(
                title="Server misconfigured!",
                color=int(c, 16),
                description="Please ask an administrator to configure it!"
            ))
            return

        # Basic self-checks
        if user.id in (ctx.user.id, self.client.user.id):
            await ctx.response.send_message(embed=Embed(description="You cannot own yourself or the bot."))
            return

        # Roles
        domme_roles = [r.id for r in ctx.user.roles]
        sub_roles = [r.id for r in user.roles]

        # Max subs check
        claim = await db.claims.find_one({"guild": ctx.guild.id, "domme": ctx.user.id})
        if claim and len(claim['submissives']) >= max_subs['value']:
            await ctx.response.send_message(embed=Embed(title="Max sub limit reached!", color=int(c, 16)))
            return

        # Only Dommes can own
        if config['value'] in domme_roles:
            await ctx.response.send_message(embed=Embed(title="Ew no.", description="Only Dommes can own someone.", color=int(c, 16)))
            return

        if any(r in domme_roles for r in [config_d['value'], config_s['value'], config_sd['value'], config_ss['value']]):
            if config_d['value'] in sub_roles:
                await ctx.response.send_message(embed=Embed(description="The person you are trying to own is a Domme, not a sub.", color=int(c, 16)))
                return

            # Consent view
            call_view = consent_view(user=user, domme=ctx.user)
            embed = Embed(description=f"""
    <a:z_point:1139692847797371030> An Ownership Request Has Arrived!
    <:p_heart39:1139692929502416926> You do not have to accept this request if you're not ready.
    <:p_heart39:1139692929502416926> Accepting this request will officially make this Domme your one and only official owner.
    <:p_heart39:1139692929502416926> Do you take this lovely Woman to be your Owner?
    """, color=int(c, 16))

            # Optional image
            try:
                consent_image = await db.custom.find_one({"guild": ctx.guild.id, "type": "consent_image"})
                show_images = await db.options.find_one({"guild": ctx.guild.id, "images": True})
                if show_images:
                    embed.set_image(consent_image['string'])
            except Exception:
                pass

            msg = await ctx.response.send_message(f"{user.mention}", embed=embed, view=call_view)
            await call_view.wait()
            if call_view.Value is True:
                # Sub accepted ownership
                return
            else:
                await ctx.send(embed=Embed(title="Declined!", description="The ownership request was declined or ignored.", color=int(c, 16)))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Please ask the owner to configure using `/settings enable`.",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
    name="disown",
    description="Disown a sub",
    nsfw=True
    )
    async def disown(self, ctx: Interaction, user: Member = SlashOption(required=False), user_id: str = SlashOption(name="id", required=False)):
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Please ask the owner to configure using `/settings enable`.",
                color=0xffa4e4
            ))
            return

        c = await self.get_color(ctx.guild.id)
        config = await db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
        config_s = await db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
        config_d = await db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
        config_sd = await db.config.find_one({"guild": ctx.guild.id, "key": "switch domme lean"})
        config_ss = await db.config.find_one({"guild": ctx.guild.id, "key": "switch sub lean"})

        # Determine target
        if user_id:
            target_id = int(user_id)
            target = await self.client.fetch_user(target_id)
        elif user:
            target = user
            target_id = user.id
        else:
            await ctx.response.send_message("Please specify a sub or user ID to disown.", ephemeral=True)
            return

        domme_roles = [r.id for r in ctx.user.roles]
        sub_roles = [r.id for r in target.roles]

        # Only Dommes can disown
        if config['value'] in domme_roles:
            await ctx.response.send_message(embed=Embed(title="Ew no.", description="Only Dommes can disown someone.", color=int(c, 16)))
            return

        claim = await db.claims.find_one({"guild": ctx.guild.id, "domme": ctx.user.id, "submissives": {"$in": [target_id]}})
        if not claim:
            await ctx.response.send_message(embed=Embed(title="Not owned", description="The person is not owned by you.", color=int(c, 16)))
            return

        await db.claims.update_one({"guild": ctx.guild.id, "domme": ctx.user.id}, {"$pull": {"submissives": target_id}})
        await ctx.response.send_message(embed=Embed(
            title=f"{target.name} has been disowned",
            description="The ownership relationship has ended. Please ensure both parties are aware.",
            color=int(c, 16)
        ))
    async def check_patron_status(self, a_token: str):
        """Check Patreon membership asynchronously."""
        url = "https://patreon.com/api/oauth2/v2/identity?include=memberships,memberships.campaign,memberships.currently_entitled_tiers&fields[member]=full_name,patron_status"
        headers = {"Authorization": f"Bearer {a_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    memberships = data.get("included")
                    if memberships:
                        for member in memberships:
                            attributes = member.get("attributes", {})
                            if attributes.get("patron_status") == "active_patron":
                                return True
        return False

    @nextcord.slash_command(name="create", description="Create your profile", nsfw=True)
    async def create(self, ctx: Interaction,
                     name: str = SlashOption(required=False),
                     bio: str = SlashOption(required=False),
                     age: int = SlashOption(required=False),
                     honorifics: str = SlashOption(required=False),
                     pet_names: str = SlashOption(required=False),
                     seeking: Literal["Yes", "No", "Maybe"] = SlashOption(required=False),
                     color: str = SlashOption(required=False),
                     pronouns: str = SlashOption(required=False),
                     pos: Literal["Domme", "Switch Domme Lean", "Switch 50/50", "Switch submissive lean", "Submissive"] = SlashOption(required=False),
                     image_url: str = SlashOption(required=False),
                     kinks: str = SlashOption(required=False),
                     limits: str = SlashOption(required=False),
                     relationship_status: str = SlashOption(required=False)):

        # Check BDSM enabled
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            return await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Use `/settings enable`.",
                color=0xffa4e4
            ))

        msg = await ctx.response.send_message("Creating profile, please wait...", ephemeral=True)

        # Check if user is a donator
        result_a = await db.donators.find_one({"user": ctx.user.id})
        if result_a:
            has_donated = await self.check_patron_status(result_a['a_token'])
            if not has_donated:
                return await msg.edit(content=None, embed=Embed(
                    title="You have not donated!",
                    description="You cannot use this command without being a verified donor.",
                    color=0xffa4e4
                ))

        # Default profile values
        profile_data = {
            "user": ctx.user.id,
            "guild": ctx.guild.id,
            "name": ctx.user.display_name,
            "bio": "This is a new profile",
            "age": 0,
            "honorifics": "N/A",
            "pet": "N/A",
            "seeking": "Maybe",
            "color": "#ffa4e4",
            "pronouns": "N/A",
            "pos": "N/A",
            "image": "https://cdn.discordapp.com/attachments/1138262120035778582/1186040407189102642/10_02A.jpg",
            "kinks": "N/A",
            "limits": "N/A",
            "relationship": "N/A"
        }

        # Update with provided options
        if name: profile_data["name"] = name
        if bio: profile_data["bio"] = bio
        if age: profile_data["age"] = age
        if honorifics: profile_data["honorifics"] = honorifics
        if pet_names: profile_data["pet"] = pet_names
        if seeking: profile_data["seeking"] = seeking
        if color:
            color = color.replace("0x", "#")
            if "#" not in color: color = "#" + color
            profile_data["color"] = color
        if pronouns: profile_data["pronouns"] = pronouns
        if pos: profile_data["pos"] = pos
        if image_url: profile_data["image"] = image_url
        if kinks: profile_data["kinks"] = kinks
        if limits: profile_data["limits"] = limits
        if relationship_status: profile_data["relationship"] = relationship_status

        # Insert or update profile
        await db.profiles.update_one(
            {"user": ctx.user.id, "guild": ctx.guild.id},
            {"$set": profile_data},
            upsert=True
        )

        updated_fields = ", ".join([k for k in profile_data if profile_data[k] != "N/A"])
        await msg.edit(content=None, embed=Embed(
            title="Profile created/updated",
            description=f"Profile updated for: {updated_fields}",
            color=0xffa4e4
        ))

    @nextcord.slash_command(name="edit", description="Edit your profile", nsfw=True)
    async def edit(self, ctx: Interaction, **kwargs):
        # Simply call `create` with provided fields to upsert
        await self.create(ctx, **kwargs)

    @nextcord.slash_command(name="profile", description="Show a user's profile", nsfw=True)
    async def profile(self, ctx: Interaction, user: Member = SlashOption(required=False)):
        user = user or ctx.user

        # Check BDSM enabled
        if not await db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            return await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description="This server is not configured for BDSM. Use `/settings enable`.",
                color=0xffa4e4
            ))

        msg = await ctx.response.send_message("Fetching profile...", ephemeral=True)

        result_p = await db.profiles.find_one({"user": user.id, "guild": ctx.guild.id})
        if not result_p:
            return await msg.edit(content=None, embed=Embed(description=f"{user.mention} has not made a profile yet!"))

        username = user.nick or await self.fetch_discord_username(user.id)
        color = result_p.get("color", "#ffa4e4")
        if "0x" not in color:
            color = "0x"+color.replace("#", "0x") if "#" in color else "0x"+color

        embed = Embed(title=f"{username}'s profile", color=int(color, 16))
        embed.description = f"""
**Nickname:** {result_p['name']}
**Age:** {result_p['age']}
**Pronouns:** {result_p['pronouns']}
**Position:** {result_p['pos']}
**Honorifics:** {result_p['honorifics']}
**Pet names:** {result_p['pet']}
**Relationship Status:** {result_p['relationship']}
**Seeking:** {result_p['seeking']}
**Kinks:** {result_p['kinks']}
**Limits:** {result_p['limits']}
**Bio:** {result_p['bio']}
"""
        embed.set_image(url=result_p['image'])
        await msg.edit(content=None, embed=embed)
    # listeners
    @commands.Cog.listener("on_message")
    async def on_tie(self, message):
        if await db.options.find_one({"guild": message.guild.id, "bdsm": True}):
            result = await db.tieup.find_one({"sub": message.author.id, "guild": message.guild.id})
            if result:
                if message.channel.id not in result['channel']:
                    await message.delete()
        else:
            return
    @commands.Cog.listener("on_message")
    async def on_badword(self, message):
        if await db.options.find_one({"guild": message.guild.id, "bdsm": True}):
            async for result in db.badwords.find({"guild": message.guild.id, "sub": message.author.id}):
                if not result:
                    return
                for word in result['words']:
                        if "*" == word:
                            continue
                        if not " " in word:
                            for substr in message.content.lower().split():
                                if "*" in word:
                                    tmp = re.compile(word.replace("*", ".*"), re.IGNORECASE)
                                    res = tmp.search(substr)
                                    if res:
                                        await message.delete()
                                        return
                                else:
                                    if word == substr.lower():
                                        await message.delete()
                                        return
                        else:
                            if "*" in word:
                                tmp = re.compile(word.replace("*", ".*"), re.IGNORECASE)
                                res = tmp.search(message.content.lower())
                                if res:
                                    await message.delete()
                                    return
                            else:
                                if word in message.content.lower():
                                    await message.delete()
                                    return
                else:
                    return
    @commands.Cog.listener("on_message")
    async def on_gag(self, message: Message):
        if await db.options.find_one({"guild": message.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": message.guild.id})
            c = color.get('string', '0xffa4e4')
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            result = await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id})
            if result:
                await message.delete()
                for k in result:
                    if k == "delete":
                        if not result['delete']:
                            break
                        else:
                            return
                        
                i = ""
                new_string = ""
                if result['gag_type'] == "mangle gag":
                    for strings in message.content:
                        choice = random.randrange(0, 100)
                        if choice >= 40:
                            new_string += strings
                        else:
                            new_string += ""
                    i = new_string
                    username = ""
                    if not message.author.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = message.author.nick
                    webhook = None
                    whs = await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id})
                    async with aiohttp.ClientSession() as session:
                        try:
                            for wh in whs['webhooks']:
                                get_webhook = Webhook.from_url(wh, session=session)
                                wh_fetch = await get_webhook.fetch()
                                get_webhook.channel_id = wh_fetch.channel_id
                                print (f"{get_webhook.channel_id}:{message.channel.id}")
                                if get_webhook.channel_id == message.channel.id:
                                    webhook = get_webhook
                                    print (webhook)
                                    break
                                else:
                                    continue
                            if not webhook:
                                avatar = None
                                if not message.author.display_avatar:
                                    avatar = message.author.default_avatar
                                else:
                                    avatar = message.author.display_avatar
                                webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                                print(webhook.channel_id)
                                print (webhook)
                                await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})

                        except Exception as e:
                            print (e)
                            avatar = None
                            if not message.author.display_avatar:
                                avatar = message.author.default_avatar
                            else:
                                avatar = message.author.display_avatar
                            webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                            print(webhook.channel_id)
                            print (webhook)
                            await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        await webhook.send(f"{i}", username=username, avatar_url=avatar.url)
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    if gag_logs:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(gag_logs['channel'])
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                    punishments = await db.config.find_one({"value": "punishments", "guild": message.guild.id})
                    if punishments:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(punishments['channel'])
                        username = ""
                        if not message.author.nick:
                            req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                            js = json.loads(req.text)
                            username = js['global_name']
                        else:
                            username = message.author.nick
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                if result["gag_type"] == "reverse gag":
                    i = message.content[::-1]
                    username = ""
                    if not message.author.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = message.author.nick
                    webhook = None
                    whs = await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id})
                    async with aiohttp.ClientSession() as session:
                        try:
                            for wh in whs['webhooks']:
                                get_webhook = Webhook.from_url(wh, session=session)
                                wh_fetch = await get_webhook.fetch()
                                get_webhook.channel_id = wh_fetch.channel_id
                                print (f"{get_webhook.channel_id}:{message.channel.id}")
                                if int(get_webhook.channel_id) == message.channel.id:
                                    webhook = get_webhook
                                    break
                                else:
                                    print ("Webhook does not exist")
                                    avatar = None
                                    if not message.author.display_avatar:
                                        avatar = message.author.default_avatar
                                    else:
                                        avatar = message.author.display_avatar
                                    webhook = await message.channel.create_webhook(name=username, avatar=avatar)

                                    webhook.channel_id = message.channel.id
                                    print (webhook)
                                    await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})
                                    break
                        except Exception as e:
                            print (e)
                            avatar = None
                            if not message.author.display_avatar:
                                avatar = message.author.default_avatar
                            else:
                                avatar = message.author.display_avatar
                            webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                            wh_fetch = await webhook.fetch()
                            webhook.channel_id = message.channel.id
                            await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        await webhook.send(f"{i}", username=username, avatar_url=avatar.url)
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    if gag_logs:
                        channel = self.client.get_channel(gag_logs['channel'])
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                    punishments = await db.config.find_one({"value": "punishments", "guild": message.guild.id})
                    if punishments:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(punishments['channel'])
                        username = ""
                        if not message.author.nick:
                            req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                            js = json.loads(req.text)
                            username = js['global_name']
                        else:
                            username = message.author.nick
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                if result["gag_type"] == "cutesy gag":
                    flags = uwuipy.uwuipy(stutter_chance=0.5, face_chance=0.2)
                    i = flags.uwuify(message.content)
                    username = ""
                    if not message.author.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = message.author.nick
                    webhook = None
                    avatar = None
                    if not message.author.display_avatar:
                        avatar = message.author.default_avatar
                    else:
                        avatar = message.author.display_avatar
                    whs = await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id})
                    async with aiohttp.ClientSession() as session:
                        try:
                            for wh in whs['webhooks']:
                                get_webhook = Webhook.from_url(wh, session=session)
                                wh_fetch = await get_webhook.fetch()
                                get_webhook.channel_id = wh_fetch.channel_id
                                print (f"{get_webhook.channel_id}:{message.channel.id}")
                                if get_webhook.channel_id == message.channel.id:
                                    webhook = get_webhook
                                    print (webhook)
                                    break
                                else:
                                    continue
                            if not webhook:
                                webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                                print(webhook.channel_id)
                                print (webhook)
                                await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})

                        except Exception as e:
                            print (e)
                            webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                            print(webhook.channel_id)
                            print (webhook)
                            await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})
                        await webhook.send(f"{i}", username=username, avatar_url=avatar.url)
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    if gag_logs:
                        channel = self.client.get_channel(gag_logs['channel'])
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                    punishments = await db.config.find_one({"value": "punishments", "guild": message.guild.id})
                    if punishments:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(punishments['channel'])
                        username = ""
                        if not message.author.nick:
                            req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                            js = json.loads(req.text)
                            username = js['global_name']
                        else:
                            username = message.author.nick
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                if result['gag_type'] == "ball gag" or result['gag_type'] == "cow gag" or result['gag_type'] == "piggy gag" or result['gag_type'] == "puppy gag" or result['gag_type'] == "kitty gag":
                    strings = message.content.split(" ")
                    for string in strings:
                        r = string.replace(string, random.choice(result['words']))
                        i += f"{r} "
                    username = ""
                    if not message.author.nick:
                        req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                        js = json.loads(req.text)
                        username = js['global_name']
                    else:
                        username = message.author.nick
                    webhook = None
                    avatar = None
                    if not message.author.display_avatar:
                        avatar = message.author.default_avatar
                    else:
                        avatar = message.author.display_avatar
                    whs = await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id})
                    async with aiohttp.ClientSession() as session:
                        try:
                            for wh in whs['webhooks']:
                                get_webhook = Webhook.from_url(wh, session=session)
                                wh_fetch = await get_webhook.fetch()
                                get_webhook.channel_id = wh_fetch.channel_id
                                print (f"{get_webhook.channel_id}:{message.channel.id}")
                                if get_webhook.channel_id == message.channel.id:
                                    webhook = get_webhook
                                    print (webhook)
                                    break
                                else:
                                    continue
                            if not webhook:
                                webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                                print(webhook.channel_id)
                                print (webhook)
                                await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})

                        except Exception as e:
                            print (e)
                            webhook = await message.channel.create_webhook(name=username, avatar=avatar)
                            print(webhook.channel_id)
                            print (webhook)
                            await db.gagged.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$push": {"webhooks": webhook.url}})
                        await webhook.send(f"{i}", username=username, avatar_url=avatar.url)
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    gag_logs = await db.config.find_one({"value": "gag_logs", "guild": message.guild.id})
                    if gag_logs:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(gag_logs['channel'])
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
                    punishments = await db.config.find_one({"value": "punishments", "guild": message.guild.id})
                    if punishments:
                        avatar = None
                        if not message.author.display_avatar:
                            avatar = message.author.default_avatar
                        else:
                            avatar = message.author.display_avatar
                        channel = self.client.get_channel(punishments['channel'])
                        username = ""
                        if not message.author.nick:
                            req = requests.get(f"https://discord.com/api/v10/users/{message.author.id}", headers={"Authorization": f"Bot {os.getenv('TOKEN')}"})
                            js = json.loads(req.text)
                            username = js['global_name']
                        else:
                            username = message.author.nick
                        await channel.send(embed=Embed(title=f"{username}", description=message.content, color=int(c, 16)).set_thumbnail(url=avatar.url))
                        return
        else:
            return
    @commands.Cog.listener("on_reaction_add")
    async def on_reaction_add(self, reaction, user):
        if await db.options.find_one({"guild": reaction.message.guild.id, "bdsm": True}):
            result = await db.gagged.find_one({"guild": reaction.message.guild.id, "sub": user.id})
            if result:
                await reaction.remove(user)
        else:
            return
    @commands.Cog.listener("on_message")
    async def on_prison_lock(self, message):
        if await db.options.find_one({"guild": message.guild.id, "bdsm": True}):
            color = await db.custom.find_one({"type": "color", "guild": message.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            
            result = await db.prison.find_one({"guild": message.guild.id, "sub": message.author.id})
            punishments = await db.config.find_one({"guild": message.guild.id, "value": "punishments"})
            rid = await db.config.find_one({"guild": message.guild.id, "key": "punishments"})
            if result:
                if punishments:
                    if message.content == result['words']:
                        emoji = self.client.get_emoji(1138216175264870400)
                        await message.add_reaction(emoji=emoji)
                        lines = result['lines'] - 1
                        if lines == 0:
                                        msg = await message.channel.send(embed=Embed(description=f"<a:prison_loading:1138685852550172703> {message.author.mention} Lines complete! Unlocking prison.. <a:prison_loading:1138685852550172703>", color=int(c, 16)))
                                        channel_list = await db.prison_channels.find_one({"guild": message.guild.id, "user": message.author.id})
                                        if isinstance(channel_list['channels'], list):
                                            
                                            for ch in channel_list['channels']:
                                                channel = self.client.get_channel(ch)
                                                await channel.set_permissions(message.author,overwrite=None)
                                        else:
                                            ch = channel_list['channels']
                                            channel = self.client.get_channel(ch)
                                            await channel.set_permissions(message.author, overwrite=None)
                                        await db.prison_channels.delete_many({"guild": message.guild.id, "user": message.author.id})
                                        if rid:
                                            role = message.guild.get_role(rid['value'])
                                            await message.author.remove_roles(role)
                                        await db.durations.delete_many({"guild": message.guild.id, "sub": message.author.id, "type": "prison"})
                                        remove(f"{message.guild.id}{message.author.id}.txt")
                                        remove(f"fmt_{message.guild.id}{message.author.id}.txt")
                                        remove(f"{message.guild.id}{message.author.id}.png")
                                        await db.prison.delete_many({"sub": message.author.id, "guild": message.guild.id})
                                        await msg.edit(embed=Embed(description=f"<:yes:1138216175264870400> {message.author.mention} Prison unlocked! You can now talk freely! <:yes:1138216175264870400>", color=int(c, 16)))
                                        return
                        channel = self.client.get_channel(punishments['channel'])
                        choice = result['words']
                        for letter in choice:
                            randbits = random.choice([True, False])
                            if randbits:
                                choice = choice.replace(letter, letter.lower())
                            else:
                                choice = choice.replace(letter, letter.upper())
                        remove(f"{message.guild.id}{message.author.id}.txt")
                        remove(f"fmt_{message.guild.id}{message.author.id}.txt")
                        remove(f"{message.guild.id}{message.author.id}.png")
                        system(f'echo "{choice}" > {message.guild.id}{message.author.id}.txt')
                        system(f"fmt {message.guild.id}{message.author.id}.txt > fmt_{message.guild.id}{message.author.id}.txt")
                        system(f"pango-view --font=\"Ldfcomicsans\" --dpi=120 -qo {message.guild.id}{message.author.id}.png fmt_{message.guild.id}{message.author.id}.txt")
                        db.prison.update_one({"guild": message.guild.id, "sub": message.author.id}, {"$set": {"words": choice, "lines": int(result['lines']-1)}})
                        fp = open(f"{message.guild.id}{message.author.id}.png", "rb")
                        file = File(fp, filename="prison.png")
                        await channel.send(f"{message.author.mention} You have been locked in prison! You must write the following lines `{result['lines']-1}` time(s)", file=file)
                    else:
                        emoji = self.client.get_emoji(1139098428715040768)
                        await message.add_reaction(emoji=emoji)
        else:
            return
# views
class consent_view(View):
    def __init__(self, user, domme):
        super().__init__(timeout=600)
        self.user = user
        self.domme = domme
        self.Value = False
    @button(style=ButtonStyle.green, custom_id="yes", label="I'd love to!", emoji="<:yes:1138216175264870400>")
    async def yes_button(self, button: Button, ctx: Interaction):
        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
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
        result = await db.claims.find_one({"guild": ctx.guild.id, "domme": domme.id, "submissives": {"$in":[user.id]}})
        if result:
            await ctx.response.send_message(embed=Embed(title="Uh oh! It seems you've already claimed that slut."),ephemeral=True)
            return
        claim_check = await db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [user.id]}})
        if claim_check:
            await ctx.response.send_message(embed=Embed(description=f"It seems {user.mention} has already been claimed by: <@{claim_check['domme']}>!", color=int(c, 16)))
            return

        if not result:
            await db.claims.update_one({"guild": ctx.guild.id, "domme": domme.id}, {"$push": {"submissives": user.id}, "$set": {"domme": domme.id}}, upsert=True)
            await ctx.response.send_message(embed=Embed(description=f"""***
<a:p_bow04:1139693034557149206> Looks like they have accepted your ownership request, babe!

May this dynamic guide you with strength, a lustful spirit, and the most exquisite relationship between both parties                                                        
***""", color=int(c, 16)))
            self.Value = True
            return
    @button(style=ButtonStyle.red, custom_id="no", label="No way!", emoji="<:no:1139098428715040768>")
    async def no_button(self, button: Button, ctx: Interaction):
        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        button.disabled = True
        if self.user != ctx.user:
            return
        await ctx.response.send_message(embed=Embed(title="Declined!", description="""
<a:prison_loading:1138685852550172703> Ownership has been declined, canceling..
""", color=int(c, 16)))
        self.Value = True
        return True
    @button(style=ButtonStyle.blurple, custom_id="cancel", label="Cancel", emoji="<:no:1139098428715040768>")
    async def cancel_button(self, button: Button, ctx: Interaction):
        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            if "#" not in c:
                c = "0x"+c
            else:
                c = c.replace("#", "0x")
        button.disabled = True
        if self.domme != ctx.user:
            return
        await ctx.response.edit_message(embed=Embed(title="Cancelled!", description="""
<a:prison_loading:1138685852550172703> Ownership has been cancelled..
""", color=int(c, 16)))
        self.value = True
        return False

def setup(client):
    client.add_cog(bdsm(client))
