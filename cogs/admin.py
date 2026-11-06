
import nextcord
import patreon
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
from requests import get
import requests
import aiohttp
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
conf = json.load(open("CONF/owners.json", "r"))
wh = json.load(open("CONF/webhooks.json", "r"))
class admin(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client

    """
    @nextcord.slash_command(
        name="restore",
        description="Restore current roles from prison in case bugged.",
        nsfw=True,
        default_member_permissions=Permissions(administrator=True)
    )
    async def restore(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to restore", required=True)):
        msg = await ctx.response.send_message("Restoring from bug...Please wait")
        try:
            punishments = db.config.find_one({"key": "punishments", "guild": ctx.guild.id})
            r = db.roles.find_one({"user": user.id, "guild": ctx.guild.id})
            for role in r['role']:
              real_role = ctx.guild.get_role(role)
              await user.add_roles(real_role)
            punish = ctx.guild.get_role(punishments['value'])
            await user.remove_roles(punish)
            await msg.edit("User resotred.")
        except Exception as e:
            print(e)
            await msg.edit(f"Error: {e}")
    // No Longer needed"""
    @nextcord.slash_command(name="safeword", description="Call the safeword (this will reset all current punishments)")
    async def safeword(self, ctx: Interaction):
        msg = await ctx.response.send_message(embed=Embed(title="Safeword has been called! Removing restrictions..", color=0x8B0000))
        gag = db.gagged.find_one_and_delete({"guild": ctx.guild.id, "sub": ctx.user.id})
        if gag:
            for wh in gag['webhooks']:
                requests.delete(wh)
        channel_list = db.prison_channels.find_one_and_delete({"guild": ctx.guild.id, "user": ctx.user.id})
        if channel_list:
            if isinstance(channel_list['channels'], list):
                                                
                for ch in channel_list['channels']:
                    channel = self.client.get_channel(ch)
                    await channel.set_permissions(ctx.user,overwrite=None)
            else:
                ch = channel_list['channels']
                channel = self.client.get_channel(ch)
            db.prison.delete_many({"sub": ctx.user.id, "guild": ctx.guild.id})
        db.badwords.delete_many({"guild": ctx.guild.id, "sub": ctx.user.id})
        result = db.chans.find_one_and_delete({"sub": ctx.user.id, "guild": ctx.guild.id})
        if result:
            text_chan = self.client.get_channel(result['text_channel'])
            await text_chan.delete()
            voice_chan = self.client.get_channel(result['voice_channel'])
            await voice_chan.delete()
            channel_list = db.channels.find_one({"guild":ctx.guild.id, "user": user.id})
            if isinstance(channel_list['channels'], list):
                                            
                for ch in channel_list['channels']:
                    channel = self.client.get_channel(ch)
                    await channel.set_permissions(user, overwrite=None)
            else:
                ch = channel_list['channels']
                channel = self.client.get_channel(ch)
                await channel.set_permissions(user,overwrite=None)
        db.tieup.delete_many({"guild": ctx.guild.id, "sub": ctx.user.id})
        await msg.edit(embed=Embed(title="**Safeword has been called! Stop playing with this individual immediately!!**", description="```All Restrictions have been removed```", color=0x8B0000).set_footer(text=f"Requester: {ctx.user.name}"))
    @nextcord.slash_command(
        name="currency", 
        description="Set the currency of the server",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def currency(self, ctx: Interaction, currency: str = SlashOption(description="Emoji and/or String to use as currency", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            db.currency.update_one({"guild": ctx.guild.id}, {"$set": {"result": f"{currency}"}}, upsert=True)
            await ctx.response.send_message(embed=Embed(
                title="Currency Updated",
                description=f"Currency has been updated to {currency}",
                color=0xffa4e4
            ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="permissions",
        description="Set permissions for who can lock people in prison (this is optional)",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def set_perms(self, ctx: Interaction, rid: nextcord.Role = SlashOption(name="role", description="Role to allow/disallow for locks in prison", required=True), allow: Literal["Yes", "No"] = SlashOption(name="allow", description="To allow or disallow", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):
            a_ret = False
            if allow == "Yes":
                a_ret = True
            else:
                a_ret = False
            db.allowed.update_one({"guild": ctx.guild.id, "role": rid.id}, {"$set": {"allow": a_ret}}, upsert=True)
            await ctx.response.send_message(embed=Embed(
                title="Allow list Updated",
                description=f"Allow list of <@&{rid.id}> has been set to {allow}",
                color=0xffa4e4
            ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for BDSM, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="update_buyable_role", 
        description="Update a buyable role on the server",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def role_Add(self, ctx: Interaction,id: str = SlashOption(description="ID to set", required=True), price: int = SlashOption(description="Price for the role to cost", required=True), role: Role = SlashOption(description="Role to make buyable!", required=True)):
        
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            if db.buyable.find_one({"guild": ctx.guild.id, "id": int(id)}):
                await ctx.response.send_message(embed=Embed(
                title="Unable to update",
                description=f"An ID already exists with this name!",
                color=0xffa4e4
            ))
            db.buyable.update_one({"guild": ctx.guild.id, "id": id}, {"$set": {"price": price, "role": role.id}}, upsert=True)
            await ctx.response.send_message(embed=Embed(
                title="Role Shop Updated",
                description=f"Role shop has been updated to {role.mention}",
                color=0xffa4e4
            ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="delete_buyable_role",
        description="Delete a buyable role",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def role_delete(self, ctx: Interaction, id: str = SlashOption(description="ID to delete from database", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            db.buyable.delete_many({"id": int(id), "guild": ctx.guild.id})
            await ctx.response.send_message(embed=Embed(
                title="Role Shop Updated",
                description=f"ID {id} has been deleted from the role shop",
                color=0xffa4e4
            ))
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(name="customize", description="Customize your embeds!", default_member_permissions=Permissions(manage_guild=True))
    async def customize(self, ctx: Interaction, db_type: Literal["color", "gag image", "status image", "consent image"] = SlashOption(name="type", description="Type of cosmetic to customize", required=True), value: str = SlashOption(name="value", description="This can either be your color (#ffffff) or an image url")):  
            if db_type == "color":
                db.custom.update_one({"guild": ctx.guild.id, "type": "color"}, {"$set": {"string": value}}, upsert=True)
            if db_type == "gag image":
                db.custom.update_one({"guild": ctx.guild.id, "type": "gag_image"}, {"$set": {"string": value}}, upsert=True)
            if db_type == "status image":
                db.custom.update_one({"guild": ctx.guild.id, "type": "status_image"}, {"$set": {"string": value}}, upsert=True)
            if db_type == "consent image":
                db.custom.update_one({"guild": ctx.guild.id, "type": "consent_image"}, {"$set": {"string": value}}, upsert=True) 
            await ctx.response.send_message(embed=Embed(title="Command executed successfully", description="Your cosmetics have been updated."))
            return
            """elif result_a:
            data = get("https://patreon.com/api/oauth2/v2/identity?include=memberships,memberships.campaign,memberships.currently_entitled_tiers&fields[member]=full_name,patron_status", headers={"Authorization": f"Bearer {result_a['a_token']}"}).json()
            try:
                memberships = data['included']
                membership = ""
                n = ""
                if memberships:
                    json_data = memberships[0]['attributes']
                    for k in json_data:
                        if k == "full_name":
                            n = json_data['full_name']
                        if k == "patron_status":
                            membership = json_data['patron_status']      
                        if membership:
                            if membership == "active_patron":
                                if db_type == "color":
                                    db.custom.update_one({"guild": ctx.guild.id, "type": "color"}, {"$set": {"string": value}}, upsert=True)
                                if db_type == "gag image":
                                    db.custom.update_one({"guild": ctx.guild.id, "type": "gag_image"}, {"$set": {"string": value}}, upsert=True)
                                if db_type == "status image":
                                    db.custom.update_one({"guild": ctx.guild.id, "type": "status_image"}, {"$set": {"string": value}}, upsert=True)
                                if db_type == "consent image":
                                    db.custom.update_one({"guild": ctx.guild.id, "type": "consent_image"}, {"$set": {"string": value}}, upsert=True)
                                
                                await ctx.response.send_message(embed=Embed(title="Command executed successfully", description="Your cosmetics have been updated."))
                                return
                            else:
                                await ctx.response.send_message(content=None, embed=Embed(title="You have not donated!", description="Oops! you have not donated and will not be able to execute this command. If you have donated, consider going through the verification again by using ``/donate``", color=0xffa4e4))
                                return
                else:
                    await ctx.response.send_message(embed=Embed(title="You have not donated!", description="Oops! you have not donated and will not be able to execute this command. If you have donated, consider going through the verification again by using ``/donate``", color=0xffa4e4))
                    return
            except KeyError as ke:
                await ctx.response.send_message(embed=Embed(title="You have not donated!", description="Oops! you have not donated and will not be able to execute this command. If you have donated, consider going through the verification again by using ``/donate``", color=0xffa4e4))
                return
        else:
            await ctx.response.send_message(embed=Embed(title="You have not donated!", description="Oops! you have not donated and will not be able to execute this command. If you have donated, consider going through the verification again by using ``/donate``", color=0xffa4e4))
            return"""
    @nextcord.slash_command(
        name="config",
        description="Config function",
        default_member_permissions=Permissions(
            manage_guild=True
        )
    )
    async def config(self, ctx: Interaction):
        pass
    @config.subcommand(
        name="bdsm",
        description="Set bdsm config value"
    )
    async def set_config(self, ctx: Interaction, key: Literal["domme", "switch domme lean","switch", "switch sub lean", "submissive", "punishments"] = SlashOption(name="key", description="Key for value", required=True), value: nextcord.Role = SlashOption(name="role", description="Role to define", required=True)):
        db.config.update_one({"guild": ctx.guild.id, "key": key}, {"$set": {"value": value.id}}, upsert=True)
        await ctx.response.send_message(embed=Embed(description=f"<@&{value.id}> set to value {key.upper()}", color=0xffa4e4))
    @nextcord.slash_command(
        name="whitelist", 
        description="White function to enable donor perms",
        default_member_permissions=Permissions(manage_guild=True),
        guild_ids=[1138262119339536496, 1139370110423937095, 1154809597161377902]
    )
    async def whitelist(self, ctx: Interaction):
        pass

    @whitelist.subcommand(
        name="add",
        description="Add a server to whitelist"
    )
    async def whitelist_add(self, ctx: Interaction, guild_id: str = SlashOption(
        name="server_id",
        description="ID of the server to whitelist.",
        required=True), reason: str = SlashOption(name="reason", description="Reason for the whitelist", required=True)):
        if not ctx.user.id in conf['owners']:
            await ctx.response.send_message(embed=Embed(
                title="You are not authorized to execute this command.",
                color=0xffa4e4
            ), ephemeral=True)
            return
        r = reason
        g = self.client.user.name
        try:
            guild = nextcord.utils.get(self.client.guilds, id=int(guild_id))
            if not guild:
                view = yeswornow(user=ctx.user, guild_id=int(guild_id), g=g, r=r, owner=ctx.user, guild_name="N/A", client=self.client)
                await ctx.response.send_message(embed=Embed(
                    title=f"You are about to add {guild_id} to the whitelist, are you sure?",
                    color=0xffa4e4
                ),
                view=view,
                ephemeral=True)
                await view.wait()

            else:
                print (guild)
                view = yeswornow(user=ctx.user, guild_id=guild.id, g=g, r=r, owner=guild.owner, guild_name=guild.name, client=self.client)
                await ctx.response.send_message(embed=Embed(
                title=f"You are about to add {guild.name} to the whitelist, are you sure?", 
                color=0xffa4e4
                ), view=view,ephemeral=True)
        except ValueError:
            await ctx.response.send_message(embed=Embed(
                title="There has been an error adding server to the whitelist.",
                color=0xffa4e4
            ), ephemeral=True)
    @whitelist.subcommand(
        name="remove",
        description="Remove a server to whitelist"
    )
    async def whitelist_remove(self, ctx: Interaction, guild_id: str = SlashOption(
        name="server_id",
        description="ID of the server to remove whitelist from.",
        required=True)):
        if not ctx.user.id in conf['owners']:
            await ctx.response.send_message(embed=Embed(
                title="You are not authorized to execute this command.",
                color=0xffa4e4
            ))
            return
        username = ""
        if ctx.user.discriminator == "0":
            username = f"{ctx.user.name}"
        else:
            username = f"{ctx.user.name}#{ctx.user.discriminator}"
        db.whitelisted.delete_many({"guild": int(guild_id)})
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(wh['whitelist'], session=session)
            current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
            await webhook.send(embed=Embed(title="Whitelist update", description=f"**{guild_id} has been removed from the whitelist**", timestamp=current_date, color=0xffa4e4).set_footer(text=f"Removed by {username} :: Timestamps are done in US/Arizona (MST)"))
        await ctx.response.send_message(embed=Embed(
                title="Whitelist updated. This action has been reported.",
                color=0xffa4e4
            ), ephemeral=True)
    @nextcord.slash_command(
        name="blacklist", 
        description="Blacklist function",
        default_member_permissions=Permissions(manage_guild=True),
        guild_ids=[1138262119339536496, 1139370110423937095, 1154809597161377902]
    )
    async def blacklist(self, ctx: Interaction):
        pass

    @blacklist.subcommand(
        name="add",
        description="Add a server to blacklist"
    )
    async def blacklist_add(self, ctx: Interaction, guild_id: str = SlashOption(
        name="server_id",
        description="ID of the server to blacklist.",
        required=True), reason: str = SlashOption(name="reason", description="Reason for the blacklist", required=True)):
        if not ctx.user.id in conf['owners']:
            await ctx.response.send_message(embed=Embed(
                title="You are not authorized to execute this command.",
                color=0xffa4e4
            ), ephemeral=True)
            return
        r = reason
        g = self.client.user.name
        try:
            guild = nextcord.utils.get(self.client.guilds, id=int(guild_id))
            if not guild:
                view = yesbornob(user=ctx.user, guild_id=int(guild_id), g=g, r=r, owner=ctx.user, guild_name="N/A", client=self.client)
                await ctx.response.send_message(embed=Embed(
                    title=f"You are about to add {int(guild_id)} to the blacklist, are you sure?",
                    color=0xffa4e4
                ),
                view=view,
                ephemeral=True)
                await view.wait()

            else:
                print (guild.id)
                view = yesbornob(user=ctx.user, guild_id=guild.id, g=g, r=r,owner=guild.owner, guild_name=guild.name, client=self.client )
                await ctx.response.send_message(embed=Embed(
                title=f"You are about to add {guild.name} to the blacklist, are you sure?", 
                color=0xffa4e4
                ), view=view,ephemeral=True)
        except ValueError:
            await ctx.response.send_message(embed=Embed(
                title="There has been an error adding server to the blacklist.",
                color=0xffa4e4
            ), ephemeral=True)
    @blacklist.subcommand(
        name="remove",
        description="Remove a server to blacklist"
    )
    async def blacklist_remove(self, ctx: Interaction, guild_id: str = SlashOption(
        name="server_id",
        description="ID of the server to blacklist.",
        required=True)):
        if not ctx.user.id in conf['owners']:
            await ctx.response.send_message(embed=Embed(
                title="You are not authorized to execute this command.",
                color=0xffa4e4
            ))
            return
        username = ""
        if ctx.user.discriminator == "0":
            username = f"{ctx.user.name}"
        else:
            username = f"{ctx.user.name}#{ctx.user.discriminator}"
        db.blacklist.delete_many({"guild": int(guild_id)})
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(wh['blacklist'], session=session)
            current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
            await webhook.send(embed=Embed(title="Blacklist update", description=f"**{guild_id} has been removed from the blacklist**", timestamp=current_date, color=0xffa4e4).set_footer(text=f"Removed by {username} :: Timestamps are done in US/Arizona (MST)"))
        await ctx.response.send_message(embed=Embed(
                title="Blacklist updated. This action has been reported.",
                color=0xffa4e4
            ), ephemeral=True)
        
class yesbornob(View):
    def __init__(self, user: Member = None, guild_id: int = None, g: str = None, r: str = None, owner: Member = None ,guild_name: str = None, client: AutoShardedClient = None):
        super().__init__(timeout=None)
        self.user = user
        self.guild_id = guild_id
        self.g = g
        self.r = r
        self.owner = owner
        self.guild_name = guild_name
        self.client = client
    @button(style=ButtonStyle.red,emoji="<:yes:1138216175264870400>", custom_id="yb", label="YES")
    async def yes_button(self, button: Button, ctx: Interaction):
        try:
            print (self.client)
            if self.guild_name == "N/A":
                self_guild_name = "No server name found"
            if self.user.id == ctx.user.id:
                username = ""
                if self.user.discriminator == "0":
                    username = f"{self.user.name}"
                else:
                    username = f"{self.user.name}#{self.user.discriminator}"
                current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
                await self.owner.send(embed=Embed(description=f"**Your server {self.guild_name} ({self.guild_id}) has been added to blacklist for {self.r}. If you feel this is an error, please open a ticket in The {self.g} Support Server**", color=0xffa4e4))
                db.blacklist.update_one({"guild": self.guild.id}, {"$set": {"reason": self.r}}, upsert=True)
                async with aiohttp.ClientSession() as session:

                    webhook = Webhook.from_url(wh['blacklist'], session=session)
                    await webhook.send(embed=Embed(title="Blacklist update", description=f"**{self.guild_name} ({self.guild_id}) for reason:** ``{self.r}``",color=0xffa4e4, timestamp=current_date).set_footer(text=f"Added by {username} :: Timestamps are done in US/Arizona (MST)"))
                await ctx.response.send_message(embed=Embed(
                    title="Blacklist updated. This action has been reported.",
                    color=0xffa4e4
                ), ephemeral=True)
                try:
                    guild = await self.client.fetch_guild(self.guild_id)
                    print (guild)
                    await self.owner.send(embed=Embed(description=f"**Your server {self.guild_name} ({self.guild_id}) has been added to blacklist for {self.r}. If you feel this is an error, please open a ticket in The {self.g} Support Server**", color=0xffa4e4))
                    await guild.leave()
                except Exception as e:
                    print (e)
                    pass
            else:
                await ctx.response.send_message(embed=Embed(title="You are not authorized.", color=0xffa4e4), ephemeral=True)
                return
        except:
            if self.user.id == ctx.user.id:
                username = ""
                if self.user.discriminator == "0":
                    username = f"{self.user.name}"
                else:
                    username = f"{self.user.name}#{self.user.discriminator}"
                current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
                db.blacklist.update_one({"guild": int(self.guild_id)}, {"$set": {"reason": self.r}}, upsert=True)
                async with aiohttp.ClientSession() as session:

                    webhook = Webhook.from_url(wh['blacklist'], session=session)
                    await webhook.send(embed=Embed(title="Blacklist update", description=f"**{self.guild_name} ({self.guild_id})for reason:** ``{self.r}``",color=0xffa4e4, timestamp=current_date).set_footer(text=f"Added by {username} :: Timestamps are done in US/Arizona (MST)"))
                await ctx.response.send_message(embed=Embed(
                    title="Blacklist updated. This action has been reported.",
                    color=0xffa4e4
                ), ephemeral=True)
                try:
                    guild = await self.client.fetch_guild(self.guild_id)
                    print (guild)
                    await self.owner.send(embed=Embed(description=f"**Your server {self.guild_name} ({self.guild_id}) has been added to blacklist for {self.r}. If you feel this is an error, please open a ticket in The {self.g} Support Server**", color=0xffa4e4))
                    await guild.leave()
                except Exception as e:
                    print (e)
                    pass
            else:
                return
    @button(style=ButtonStyle.green, emoji="<:no:1139098428715040768>", custom_id="nb", label="NO")
    async def no_button(self, button: Button, ctx: Interaction):
        if self.user.id == ctx.user.id:
            username = ""
            if self.user.discriminator == "0":
                username = f"{self.user.name}"
            else:
                username = f"{self.user.name}#{self.user.discriminator}"
            await ctx.response.send_message(embed=Embed(
                color=0xffa4e4,
                title="Blacklist canceled by Owner",
                description=f"{username} has cancelled the blacklist"
            ))
        else:
            return
class yeswornow(View):
    def __init__(self, user: Member = None, guild_id: int = None , g: str = None, r: str = None, owner: Member = None, guild_name: str = None, client: AutoShardedClient = None):
        super().__init__(timeout=None)
        self.user = user
        self.guild_id = guild_id
        self.g = g
        self.r = r
        self.owner = owner
        self.guild_name = guild_name
        self.client = client
    @button(style=ButtonStyle.red,emoji="<:yes:1138216175264870400>", custom_id="yw", label="YES")
    async def yes_button(self, button: Button, ctx: Interaction):
        try:
            if self.guild_name == "N/A":
                self.guild_name = "No server name found"
            print (self.owner)
            if self.user.id == ctx.user.id:
                username = ""
                if self.user.discriminator == "0":
                    username = f"{self.user.name}"
                else:
                    username = f"{self.user.name}#{self.user.discriminator}"
                current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
                db.whitelisted.update_one({"guild": self.guild_id}, {"$set": {"reason": self.r}}, upsert=True)
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(wh['whitelist'], session=session)
                    await webhook.send(embed=Embed(title="Whitelist update", description=f"**{self.guild_name} ({self.guild_id}) for reason:** ``{self.r}``",color=0xffa4e4, timestamp=current_date).set_footer(text=f"Added by {username} :: Timestamps are done in US/Arizona (MST)"))
                await ctx.response.send_message(embed=Embed(
                    title="Whitelist updated. This action has been reported.",
                    color=0xffa4e4
                ), ephemeral=True)
                try:
                    guild = await self.client.fetch_guild(self.guild_id)
                    await guild.owner.send(embed=Embed(description=f"**Your server {self.guild_name} ({self.guild_id}) has been added to whitelist for {self.r}! Everyone in your server can now use donator commands**", color=0xffa4e4))
                except Exception as e:
                    print (e)
                    pass
            else:
                await ctx.response.send_message(embed=Embed(title="You are not authorized.", color=0xffa4e4), ephemeral=True)
                return
        except Exception as se:
            print (se)
            if self.user.id == ctx.user.id:
                username = ""
                if self.user.discriminator == "0":
                    username = f"{self.user.name}"
                else:
                    username = f"{self.user.name}#{self.user.discriminator}"
                current_date = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(tz=pytz.timezone("US/Arizona"))
                db.whitelisted.update_one({"guild": int(self.guild_id)}, {"$set": {"reason": self.r}}, upsert=True)
                async with aiohttp.ClientSession() as session:

                    webhook = Webhook.from_url(wh['whitelist'], session=session)
                    await webhook.send(embed=Embed(title="Whitelist update", description=f"**{self.guild_name} ({self.guild_id}) for reason:** ``{self.r}``",color=0xffa4e4, timestamp=current_date).set_footer(text=f"Added by {username} :: Timestamps are done in US/Arizona (MST)"))
                await ctx.response.send_message(embed=Embed(
                    title="Whitelist updated. This action has been reported.",
                    color=0xffa4e4
                ), ephemeral=True)
            else:
                return
    @button(style=ButtonStyle.green, emoji="<:no:1139098428715040768>", custom_id="nw", label="NO")
    async def no_button(self, button: Button, ctx: Interaction):
        if self.user.id == ctx.user.id:
            username = ""
            if self.user.discriminator == "0":
                username = f"{self.user.name}"
            else:
                username = f"{self.user.name}#{self.user.discriminator}"
            await ctx.response.send_message(embed=Embed(
                color=0xffa4e4,
                title="Whitelist canceled by Owner",
                description=f"{username} has cancelled the whitelist"
            ))
        else:
            return
def setup(client):
    client.add_cog(admin(client))
