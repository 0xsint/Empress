from nextcord import Intents
from nextcord import Interaction, Embed, Activity, ActivityType
from dotenv import load_dotenv
import os
import unicodedata
import asyncio
from asyncio import sleep
from nextcord.ext.commands import AutoShardedBot, Bot
from nextcord.ext import commands
import aiohttp
import pymongo
import random
from cogs.timers import timers
from nextcord import Webhook
from requests import get, delete
load_dotenv(dotenv_path="/root/as.env")
intents = Intents.default()
intents.message_content = True
intents.guilds = True
client = AutoShardedBot(command_prefix=".", help_command=None, intents=intents)
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
cogs = []
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        cogs.append("cogs." + filename[:-3])
if __name__ == '__main__':
    for cog in cogs:
        client.load_extension(cog)
        print (cog)
async def snipe_loop():
    await client.wait_until_ready()
    print("snipe_ready")

    while not client.is_closed():
        try:
            # Iterate over guilds safely
            for guild in list(client.guilds):
                try:
                    # Fetch snipes in a background thread (MongoDB is blocking)
                    snipes = await asyncio.to_thread(
                        lambda: list(db.messages.find({"guild": guild.id}))
                    )

                    print(f"[{guild.name}] Found {len(snipes)} snipes")

                    # Loop through each snipe safely
                    for snipe in snipes:
                        duration = snipe.get("duration", 0)

                        if duration <= 0:
                            await asyncio.to_thread(
                                lambda: db.messages.delete_one({"_id": snipe["_id"]})
                            )
                            continue

                        result = await asyncio.to_thread(
                            lambda: db.messages.update_one(
                                {"_id": snipe["_id"]},
                                {"$inc": {"duration": -1}}
                            )
                        )

                        if result.modified_count > 0:
                            print(f"Updated snipe {_id} for guild {guild.id}")

                        # Yield after each update to prevent blocking
                        await asyncio.sleep(0)

                except Exception as inner_e:
                    print(f"Error in snipe_loop for guild {guild.id}: {inner_e}")

            print("snipe_loop cycle complete")
            await asyncio.sleep(120)

        except Exception as e:
            print("Main snipe_loop error:", e)
            await asyncio.sleep(5)
@client.slash_command(
name="invite",
description="For the invite of the bot")
async def get_invite(ctx: Interaction):
        await ctx.response.send_message(embed=Embed(description=f"To invite me to your server [click here](https://discord.com/api/oauth2/authorize?client_id=741209127103234078&permissions=8&scope=bot%20applications.commands)"))
async def tasks_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        guilds = client.guilds
        members = 0
        await client.change_presence(activity=Activity(type=ActivityType.watching, name=f"over subs in {len(client.guilds)} servers"))
        await sleep(120)
@client.command(name="sync")
@commands.is_owner()
async def sync_com(ctx: commands.Context):
     msg = await ctx.message.reply("Syncing the timers now.. (dev command)")
     client.loop.create_task(timers_loop())
     client.loop.create_task(tasks_loop())
     await msg.edit("Timers and Functions synced")
     return
@client.event
async def on_ready():
    db.cooldowns.delete_many({})
    db.bet_sleeps.delete_many({})
    db.levels_sleep.delete_many({})
import asyncio
import os
import aiohttp
from nextcord import Webhook, Embed

# helper: run blocking DB call in thread
async def db_find_list(collection, query):
    return await asyncio.to_thread(lambda: list(collection.find(query)))

async def db_find_one(collection, query):
    return await asyncio.to_thread(lambda: collection.find_one(query))

async def db_update_one(collection, filter_q, update_q, upsert=False):
    return await asyncio.to_thread(lambda: collection.update_one(filter_q, update_q, upsert=upsert))

async def db_delete_one(collection, query):
    return await asyncio.to_thread(lambda: collection.delete_one(query))

async def safe_remove_file(path):
    try:
        await asyncio.to_thread(lambda: os.remove(path) if os.path.exists(path) else None)
    except Exception as e:
        print(f"Error removing {path}: {e}")

async def safe_fetch_member(guild, member_id, timeout=10):
    try:
        return await asyncio.wait_for(guild.fetch_member(member_id), timeout=timeout)
    except Exception as e:
        # could be NotFound, TimeoutError, HTTPException, etc
        return None

async def safe_create_webhook(channel, name, timeout=10):
    try:
        return await asyncio.wait_for(channel.create_webhook(name=name), timeout=timeout)
    except Exception as e:
        print(f"create_webhook failed for channel {channel}: {e}")
        return None

async def safe_delete_webhook(webhook_url, session, token, timeout=10):
    try:
        wh = await asyncio.wait_for(Webhook.from_url(webhook_url, session=session, bot_token=token), timeout=timeout)
        await asyncio.wait_for(wh.delete(), timeout=timeout)
    except Exception as e:
        print(f"safe_delete_webhook error: {e}")

async def timers_loop():
    await client.wait_until_ready()
    print("timers_ready")
    token = os.getenv("TOKEN")

    # reuse a single aiohttp session across iterations
    async with aiohttp.ClientSession() as session:
        while not client.is_closed():
            try:
                # iterate guilds
                for guild in client.guilds:
                    # --- gag handling ---
                    gag_list = await db_find_list(db.durations, {"guild": guild.id, "type": "gag"})
                    for gag in gag_list:
                        try:
                            new_duration = gag.get('duration', 0) - 1
                            await db_update_one(db.durations, {"guild": guild.id, "type": "gag", "sub": gag['sub']},
                                                {"$set": {"duration": new_duration}})
                            if new_duration <= 1:
                                # expired soon - handle deletion
                                results = await db_find_one(db.gagged, {"sub": gag['sub'], "guild": guild.id})
                                if results:
                                    webhooks = results.get('webhooks', [])
                                    for wh_url in webhooks:
                                        await safe_delete_webhook(wh_url, session, token)
                                    await db_delete_one(db.durations, {"sub": gag['sub'], "type": "gag", "guild": guild.id})
                                    await db_delete_one(db.gagged, {"sub": gag['sub'], "guild": guild.id})
                                continue
                        except Exception as e:
                            print(f"Error processing gag for guild {guild.id}: {e}")
                            # attempt to clean up bad gag doc
                            await db_delete_one(db.gagged, {"sub": gag.get('sub'), "guild": guild.id})
                            continue

                    # --- prison handling ---
                    prison_list = await db_find_list(db.durations, {"guild": guild.id, "type": "prison"})
                    for prison in prison_list:
                        try:
                            sub_id = prison.get('sub')
                            new_duration = prison.get('duration', 0) - 1
                            await db_update_one(db.durations, {"guild": guild.id, "type": "prison", "sub": sub_id},
                                                {"$set": {"duration": new_duration}})
                            if new_duration <= 1:
                                continue

                            member = await safe_fetch_member(guild, sub_id)
                            if not member:
                                # cleanup if member can't be fetched
                                await db_delete_one(db.prison, {"sub": sub_id, "guild": guild.id})
                                await db_delete_one(db.prison_channels, {"user": sub_id, "guild": guild.id})
                                continue

                            channels = await db_find_one(db.prison_channels, {"user": sub_id, "guild": guild.id})
                            if not channels:
                                # remove role and cleanup files safely
                                punish_cfg = await db_find_one(db.config, {"key": "punishments", "guild": guild.id})
                                role = guild.get_role(punish_cfg['value']) if punish_cfg else None
                                if role:
                                    try:
                                        await asyncio.wait_for(member.remove_roles(role), timeout=10)
                                    except Exception:
                                        pass
                                # remove files via thread (non-blocking)
                                await safe_remove_file(f"{guild.id}{member.id}.png")
                                await safe_remove_file(f"{guild.id}{member.id}.txt")
                                await safe_remove_file(f"fmt_{guild.id}{member.id}.txt")
                                continue

                            # set permissions removal logic (example for list vs single)
                            if isinstance(channels.get('channels'), list):
                                for chan_id in channels['channels']:
                                    channel = client.get_channel(chan_id)
                                    if not channel:
                                        continue
                                    try:
                                        await asyncio.wait_for(channel.set_permissions(member, overwrite=None), timeout=10)
                                    except Exception:
                                        pass
                            else:
                                chan_id = channels.get('channels')
                                channel = client.get_channel(chan_id)
                                if channel:
                                    try:
                                        await asyncio.wait_for(channel.set_permissions(member, overwrite=None), timeout=10)
                                    except Exception:
                                        pass

                            # remove role, files, and DB documents
                            punish_cfg = await db_find_one(db.config, {"key": "punishments", "guild": guild.id})
                            role = guild.get_role(punish_cfg['value']) if punish_cfg else None
                            if role:
                                try:
                                    await asyncio.wait_for(member.remove_roles(role), timeout=10)
                                except Exception:
                                    pass

                            await safe_remove_file(f"{guild.id}{member.id}.png")
                            await safe_remove_file(f"{guild.id}{member.id}.txt")
                            await safe_remove_file(f"fmt_{guild.id}{member.id}.txt")

                            await db_delete_one(db.prison_channels, {"user": sub_id, "guild": guild.id})
                            await db_delete_one(db.prison, {"sub": sub_id, "guild": guild.id})
                            await db_delete_one(db.durations, {"sub": sub_id, "type": "prison", "guild": guild.id})
                        except Exception as e:
                            print(f"Error processing prison for guild {guild.id}, sub {prison.get('sub')}: {e}")

                    # --- task handling (similar pattern) ---
                    task_durs = await db_find_list(db.durations, {"guild": guild.id, "type": "task"})
                    for dur in task_durs:
                        try:
                            if not dur:
                                break
                            task = await db_find_one(db.task_list, {"guild": guild.id, "domme": dur['domme'], "sub": dur['sub'], "task_id": dur['task_id']})
                            if not task:
                                continue

                            # decrement duration
                            if dur.get('duration', 0) <= 1:
                                new_duration = dur.get('duration', 0) - 1
                                await db_update_one(db.durations, {"guild": guild.id, "type": "task", "domme": dur['domme'], "sub": dur['sub'], "task_id": dur['task_id']},
                                                    {"$set": {"duration": new_duration}})
                                continue

                            pun = task.get('punishment', '').lower()
                            if pun == "gag":
                                words = ["mmmmmf", "mmmmph", "mmph", "mmmmphh", "mmmmf", "mphhh~"]
                                chan = await safe_fetch_channel(task['channel'])
                                if chan:
                                    webhook = await safe_create_webhook(chan, name=f"Webhook Task {task['sub']}")
                                    if webhook:
                                        # store webhook url and set gag
                                        await db_update_one(db.gagged, {"guild": guild.id, "sub": task['sub']},
                                                            {"$set": {"words": words, "gag_type": "ball gag", "delete": False, "webhooks": [webhook.url]}}, upsert=True)
                                        await db_update_one(db.durations, {"guild": guild.id, "sub": task['sub'], "type": "gag"},
                                                            {"$set": {"duration": 1200, "full_duration": 1200, "task_id": random.randrange(0, 99999)}}, upsert=True)
                            # ... other punishments (dm, announce, etc) - use safe_fetch_member and safe channel fetches
                            await db_delete_one(db.task_list, {"guild": guild.id, "domme": task['domme'], "sub": task['sub'], "task_id": task['task_id']})
                        except Exception as e:
                            print(f"task handling error: {e}")

                # end guild loop

                print("timers_completed")
            except Exception as outer_e:
                print(f"Unexpected error in timers_loop: {outer_e}")

            # yield & sleep a bit before next pass
            await asyncio.sleep(2)   # small yield; you can switch to sleep(120) like before when everything stable
client.loop.create_task(timers_loop())
client.loop.create_task(tasks_loop())
client.loop.create_task(timers.snipe_loop(client))
client.run(os.getenv("TOKEN"))