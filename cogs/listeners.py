from nextcord import *
from dotenv import load_dotenv
import os
from nextcord.ext import commands
import motor.motor_asyncio
import random
import json
import asyncio
from pbkdf2 import PBKDF2
import pyaes
from cogs.timers import timers
import secrets
from uuid import uuid4
import binascii
import aiohttp

load_dotenv()

# Use Motor instead of pymongo
mongodb = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage


def decrypt(passphrase: str, salt: bytes, iv: int, data: bytes):
    key = PBKDF2(passphrase, salt).read(32)
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    dm = aes.decrypt(binascii.unhexlify(data))
    try:
        return dm.decode()
    except UnicodeDecodeError:
        return "UNABLE TO DECRYPT"


def encrypt(data):
    passkey = os.getenv("ENCRYPT_PASS")
    salt = os.urandom(16)
    iv = secrets.randbits(256)
    key = PBKDF2(passkey, salt).read(32)
    aes = pyaes.AESModeOfOperationCTR(key, pyaes.Counter(iv))
    ciphertext = aes.encrypt(data)
    c = binascii.hexlify(ciphertext)
    return {
        "passphrase": str(binascii.hexlify(key)),
        "pass_bytes": binascii.hexlify(key),
        "iv": str(iv),
        "str_data": str(c),
        "bytes_data": binascii.hexlify(ciphertext),
        "salt": salt
    }


class listeners(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    @slash_command(
        name="snipe",
        description="Snipe a deleted message"
    )
    async def snipe(self, ctx: Interaction, index: int = SlashOption(name="index", description="Message to index", default=0, required=False)):
        msg = await ctx.response.send_message("Fetching snipe...", ephemeral=False)

        color = await db.custom.find_one({"type": "color", "guild": ctx.guild.id})
        c = color['string']
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else "0x" + c

        results = [r async for r in db.messages.find({"guild": ctx.guild.id, "channel": ctx.channel.id})]
        if not results:
            await msg.edit(content="No snipes found.")
            return

        if index != 0:
            result = results[int(index - 1)]
        else:
            result = results[-1]

        member = await ctx.guild.fetch_member(result['user'])

        try:
            content = decrypt(os.getenv("ENCRYPT_PASS"), result['salt'], int(result['iv']), result['content'])
        except Exception:
            content = "Unable to decrypt message"

        await msg.edit(content="", embed=Embed(
            title=f"Snipe of {member.global_name}",
            color=int(c, 16),
            description=content
        ).set_footer(text=f"Snipe {index if index else len(results)} of {len(results)}."))

    @commands.Cog.listener("on_message")
    async def on_level_up(self, message):
        if not message.guild or message.author.bot:
            return

        options = await db.options.find_one({"guild": message.guild.id, "levels": True})
        if not options:
            return

        color_doc = await db.custom.find_one({"type": "color", "guild": message.guild.id})
        c = color_doc['string']
        if "0x" not in c:
            c = c.replace("#", "0x") if "#" in c else "0x" + c

        if await db.levels_sleep.find_one({"user": message.author.id, "guild": message.guild.id}):
            return

        result = await db.levels.find_one({"member": message.author.id, "guild": message.guild.id})
        if not result:
            return

        level = result['level']
        exp = result['exp']
        new_exp = exp + random.randrange(40, 100)
        lvl_end = int(new_exp / 100)

        if level < lvl_end:
            level = lvl_end
            bal = 50 * level
            await db.balance.update_one({"guild": message.guild.id, "user": message.author.id}, {"$inc": {"balance": bal}}, upsert=True)
            await db.levels.update_one({"member": message.author.id, "guild": message.guild.id}, {"$set": {"level": level, "exp": 0}})
            embed = Embed(description=f"**Congratulations {message.author.mention}! Level up to level: {level}**", color=0xffa4e4)

            async for doc in db.levels_reward.find({"guild": message.guild.id}):
                if doc and level == doc['level']:
                    role = message.guild.get_role(doc['role'])
                    await message.author.add_roles(role)
                    embed.add_field(name=f"Level reward for level {level}", value=f"You earned: {role.mention}", inline=True)
                    break

            res = await db.config.find_one({"value": "levels", "guild": message.guild.id})
            chan = self.client.get_channel(res['channel']) if res else message.channel
            await chan.send(embed=embed)

            await db.levels_sleep.insert_one({"user": message.author.id, "guild": message.guild.id})
            await asyncio.sleep(3)
            await db.levels_sleep.delete_many({"user": message.author.id, "guild": message.guild.id})
        else:
            updated_exp = random.randrange(1, 40)
            await db.levels.update_one({"member": message.author.id, "guild": message.guild.id}, {"$inc": {"exp": updated_exp}})
            await db.levels_sleep.insert_one({"user": message.author.id, "guild": message.guild.id})
            await asyncio.sleep(6)
            await db.levels_sleep.delete_many({"user": message.author.id, "guild": message.guild.id})

    @commands.Cog.listener("on_message_delete")
    async def store_message(self, message):
        if message.author.bot:
            return
        if await db.gagged.find_one({"guild": message.guild.id, "sub": message.author.id}):
            return

        encrypted_message = encrypt(message.content.encode())
        c_id = str(uuid4())
        await db.messages.insert_one({
            "user": message.author.id,
            "guild": message.guild.id,
            "_id": c_id,
            "content": encrypted_message['bytes_data'],
            "duration": 1200,
            "channel": message.channel.id,
            "salt": encrypted_message['salt'],
            "iv": encrypted_message['iv']
        })

    @commands.Cog.listener("on_guild_join")
    async def check_blacklist(self, guild):
        result = await db.blacklist.find_one({"guild": guild.id})
        if result:
            await guild.owner.send(embed=Embed(
                title="You are on the blacklist!",
                description=f"You are blacklisted for {result['reason']}. Contact support if this is an error.",
                color=0xffa4e4
            ))
            await guild.leave()
        else:
            await guild.system_channel.send(embed=Embed(
                description=f"Hello! I am <@{self.client.user.id}> — use `/config bdsm` or `/set channel` to get started!",
                color=0xffa4e4
            ))


def setup(client):
    client.add_cog(listeners(client))