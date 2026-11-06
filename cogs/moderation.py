import requests
import nextcord
from nextcord import *
from nextcord.ui import Button, button, View
from dotenv import load_dotenv
import os
import aiohttp
from nextcord.ext import application_checks
from nextcord.ext import commands
import pymongo
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class moderation(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    
    @nextcord.slash_command(
        name="set",
        description="Set module",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def set_func(self, ctx: Interaction):
        pass
    @set_func.subcommand(name="max_subs", description="Set maximum subs on claims")
    async def max_subs(self, ctx: Interaction, max_subs: int = SlashOption(name="max", description="Maximum subs to set", required=True)):
        db.config.update_one({"guild": ctx.guild.id, "key": "max subs"}, {"$set": {"value": max_subs}}, upsert=True)
        await ctx.response.send_message(embed=Embed(description=f"The maximum submissives able to claim per Domme is now ``{max_subs}``.", color=0x8B0000))
    @set_func.subcommand(
        name="level",
        description="Set a level for a user",
    )
    @application_checks.has_guild_permissions(manage_guild=True)
    async def level_set(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to set level of", required=True), level: int = SlashOption(name="level", description="What to set the user's level to, please don't use this parameter if you want to reset", required=False)):
        if db.options.find_one({"guild": ctx.guild.id, "levels": True}):
            if not level:
                level = 1
            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(
                    color=0x8B0000,
                    description="Sorry, you can't set the level of yourself, if this is an emergency, please contact an Administator."
                ), ephemeral=True)
                return

            db.levels.update_one({"guild": ctx.guild.id, "member": user.id}, {"$set": {"level": level, "exp": 0}})
            await ctx.response.send_message(
                embed=Embed(color=0x8B0000, description=f"{user.mention}'s level has been set to {level}.")
            , ephemeral=True)
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for levels, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0x8B0000
                    ))
    @set_func.subcommand(
        name="channel",
        description="Set a channel for level up"
    )
    @application_checks.has_guild_permissions(manage_guild=True)
    async def channel_set(self, ctx: Interaction, channel: TextChannel = SlashOption(name="channel", description="Channel to set level to redirect to", required=True), value: Literal["punishments", "levels", "gag_logs"] = SlashOption(name="value", description="Channel type", required=True)):
        db.config.update_one({"guild": ctx.guild.id, "value": value}, {"$set": {"channel": channel.id}}, upsert=True)
        await ctx.response.send_message(
            embed=Embed(color=0x8B0000, description=f"The {value.upper()} channel has been set to {channel.mention}.")
        , ephemeral=True)
    @nextcord.slash_command(name="force_ungag", default_member_permissions=Permissions(manage_messages=True), description="Force ungag a sub if bugged")
    async def force_ungag(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to ungag", required=True)):
        
        result = db.gagged.find_one_and_delete({"guild": ctx.guild.id, "sub": user.id})
        db.durations.delete_many({"guild": ctx.guild.id, "sub": user.id, "type": "gag"})
        await ctx.response.send_message(embed=Embed(description=f"{user.mention} ungagged by an administrator.", color=0x8B0000))
        for wh in result['webhooks']:
            requests.delete(wh)
    @nextcord.slash_command(name="force_untie", default_member_permissions=Permissions(manage_messages=True), description="Force untie a sub if bugged")
    async def force_untie(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to ungag", required=True)):
        
        result = db.tieup.find_one_and_delete({"guild": ctx.guild.id, "sub": user.id})
        await ctx.response.send_message(embed=Embed(description=f"{user.mention} untied by an administrator.", color=0x8B0000))
    @nextcord.slash_command(name="force_badword", default_member_permissions=Permissions(manage_messages=True), description="Force clear badwords from a sub if bugged")
    async def force_badword(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to ungag", required=True)):
        result = db.badwords.find_one_and_delete({"guild": ctx.guild.id, "sub": user.id})
        await ctx.response.send_message(embed=Embed(description=f"{user.mention} has had all badwords cleared by an administrator.", color=0x8B0000))
    @nextcord.slash_command(name="force_unlock", default_member_permissions=Permissions(manage_messages=True), description="Force unlock a sub's prison if bugged")
    async def force_unlock(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to Unlock", required=True)):
        try:
            msg = await ctx.response.send_message(embed=Embed(description=f"Unlocking {user.mention} by administrative privilege", color=0x8B0000))
            
            punishments = db.config.find_one({"key": "punishments", "guild": ctx.guild.id})
            result = db.prison.find_one_and_delete({"guild": ctx.guild.id, "sub": user.id})
            r = db.roles.find_one({"user": user.id, "guild": ctx.guild.id})
            channel_list = db.prison_channels.find_one({"guild": ctx.guild.id, "user": user.id})

            if isinstance(channel_list['channels'], list):
                        for ch in channel_list['channels']:
                            overwrites = {
                                user: PermissionOverwrite(view_channel=True)
                            }
                            channel = self.client.get_channel(ch)
                            await channel.set_permissions(user,overwrite=None)
            else:
                        ch = channel_list['channels']
                        overwrites = {
                                user: PermissionOverwrite(view_channel=True)
                            }
                        channel = self.client.get_channel(ch)
                        
                        await channel.set_permissions(user, overwrite=None)
            punish = ctx.guild.get_role(punishments['value'])
            await user.remove_roles(punish)
            db.durations.delete_many({"guild": ctx.guild.id, "sub": user.id, "type": "prison"})
            await msg.edit(embed=Embed(description=f"{user.mention}'s prison unlocked by an administrator.", color=0x8B0000)) 
        except Exception as e:
            print (e)
            await ctx.followup.send(embed=Embed(description=f"I may have ran into an error! {e}", color=0x8B0000))
    @nextcord.slash_command(name="force_remove_blindfold", default_member_permissions=Permissions(manage_messages=True), description="Force unlock a sub's prison if bugged")
    async def force_remove_blindfold(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to Unlock", required=True)):
        try:
            msg = await ctx.response.send_message(embed=Embed(description=f"Removing blindfold {user.mention} by administrative privilege", color=0x8B0000))
            
            result = db.chans.find_one_and_delete({"guild": ctx.guild.id, "sub": user.id})
            r = db.blind_roles.find_one({"user": user.id, "guild": ctx.guild.id})
            channel_list = db.channels.find_one({"guild": ctx.guild.id, "user": user.id})
            if isinstance(channel_list['channels'], list):
                        for ch in channel_list['channels']:
                            overwrites = PermissionOverwrite()
                            overwrites.view_channel = True
                            channel = self.client.get_channel(ch)
                            await channel.set_permissions(user, overwrite=None)
            else:
                        ch = channel_list['channels']
                        overwrites = PermissionOverwrite()
                        overwrites.view_channel = True
                        channel = self.client.get_channel(ch)
                        await channel.set_permissions(user, overwrite=None)
            channel = self.client.get_channel(result['text_channel'])
            await channel.delete()
            voice_channel = self.client.get_channel(result['voice_channel'])
            await voice_channel.delete()
            await msg.edit(embed=Embed(description=f"{user.mention}'s blindfold has been removed by an administrator", color=0x8B0000)) 
        except Exception as e:
            print (e)
            await ctx.followup.send(embed=Embed(description=f"I may have ran into an error! {e}", color=0x8B0000))
    @nextcord.slash_command(
        name="delete_from_db",
        description="Delete a user from the listing database",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def delete_from_db(self, ctx: Interaction,db_type: Literal["gag", "badword", "prison", "tied up"] = SlashOption(name="type", required=True, description="Type of DB to query"), user: str = SlashOption(name="user_id", description="User ID to delete", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):

            view = yes_rg_or_no_rg(ctx.user, user, db_type)
            try:
                await ctx.response.send_message(embed=Embed(
                color=0x8B0000,
                description=f"You are about to delete {user} from the DB of {db_type.upper()}, are you sure?"
                ), view=view)
                if view.Value == True:
                    return
                else:
                    await ctx.response.edit_message(embed=Embed(
                        title="Canceled",
                        description="A timeout has occurred, command cancelled!",
                        color=0x8B0000
                    ))
                    return
            except TimeoutError as te:
                await ctx.response.edit_message(embed=Embed(
                        title="Canceled",
                        description="A timeout has occurred, command cancelled!",
                        color=0x8B0000
                    ))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for BDSM, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0x8B0000
                    ))
    @nextcord.slash_command(
        name="reset",
        description="Reset someone's ownership status",
        default_member_permissions=Permissions(manage_guild=True)
    )
    async def reset_own(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to reset their ownership", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "bdsm": True}):

            view = yesorno(ctx.user, user)
            try:
                await ctx.response.send_message(embed=Embed(
                color=0x8B0000,
                description=f"You are about to reset {user.mention}'s ownership status, are you sure?"
                ), view=view)
                if view.Value == True:
                    return
                else:
                    await ctx.response.edit_message(embed=Embed(
                        title="Canceled",
                        description="A timeout has occurred, command cancelled!",
                        color=0x8B0000
                    ))
                    return
            except TimeoutError as te:
                await ctx.response.edit_message(embed=Embed(
                        title="Canceled",
                        description="A timeout has occurred, command cancelled!",
                        color=0x8B0000
                    ))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for BDSM, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0x8B0000
                    ))
class yesorno(View):
    def __init__(self, user, sub):
        super().__init__(timeout=600)
        self.user = user
        self.sub = sub
        
        self.Value = False

    @button(style=ButtonStyle.red,emoji="<:yes:1138216175264870400>", custom_id="y", label="YES")
    async def yes_button(self, button: Button, ctx: Interaction):
        if self.user.id == ctx.user.id:
            result = db.claims.find_one({"guild": ctx.guild.id, "submissives": {"$in": [self.sub.id]}})
            if result:
                db.claims.update_one({"guild": ctx.guild.id, "submissives": {"$in": [self.sub.id]}}, {"$pull": {"submissives": {"$in": [self.sub.id]}}})
                embed = Embed(description=f"**{self.sub.mention}'s ownership status has been reset.**", color=0x8B0000)
                await ctx.response.send_message(embed=embed)
                self.Value = True
                return True
            else:
                await ctx.response.send_message(embed=Embed(
                    color=0x8B0000,
                    title="Sub was found to not have an Owner!"
                ))
                self.Value = True
                return True
            

        else:
            await ctx.response.send_message(embed=Embed(title="You are not authorized.", color=0x8B0000), ephemeral=True)
            self.Value = True
            return True
    @button(style=ButtonStyle.green, emoji="<:no:1139098428715040768>", custom_id="n", label="NO")
    async def no_button(self, button: Button, ctx: Interaction):
        self.Value = True
        await ctx.response.send_message(embed=Embed(
            color=0x8B0000,
            title="Reset cancelled!, Administrator selected no."
        ))
class yes_rg_or_no_rg(View):
    def __init__(self, user, sub, db_type):
        super().__init__(timeout=600)
        self.user = user
        self.sub = sub
        self.db_type = db_type
        self.Value = False
    @button(style=ButtonStyle.red,emoji="<:yes:1138216175264870400>", custom_id="y", label="YES")
    async def yes_button(self, button: Button, ctx: Interaction):
        if self.user.id == ctx.user.id:
            if self.db_type == "gag":
                result = db.gagged.find_one({"guild": ctx.guild.id, "sub": int(self.sub)})
                if result:
                    async with aiohttp.ClientSession() as session:
                        await Webhook.from_url(result['webhook'], session=session).delete()
                    db.gagged.delete_many({"guild": ctx.guild.id, "sub": int(self.sub)})
                    embed = Embed(description=f"**{self.sub} has been deleted from the DB {self.db_type}**", color=0x8B0000)
                    await ctx.response.send_message(embed=embed)
                    self.Value = True
                    return True
                else:
                    await ctx.response.send_message(embed=Embed(
                        color=0x8B0000,
                        title="Sub was not found to be gagged!"
                    ))
                    self.Value = True
                    return True
            if self.db_type == "prison":
                result = db.prison.find_one({"guild": ctx.guild.id, "sub": int(self.sub)})
                if result:
                    db.prison.delete_many({"guild": ctx.guild.id, "sub": int(self.sub)})
                    embed = Embed(description=f"**{self.sub} has been deleted from the DB {self.db_type}**", color=0x8B0000)
                    await ctx.response.send_message(embed=embed)
                    self.Value = True
                    return True
                else:
                    await ctx.response.send_message(embed=Embed(
                        color=0x8B0000,
                        title="Sub was not found to be locked!"
                    ))
                    self.Value = True
                    return True
            if self.db_type == "badword":
                result = db.badwords.find_one({"guild": ctx.guild.id, "sub": int(self.sub)})
                if result:
                    db.badwords.delete_many({"guild": ctx.guild.id, "sub": int(self.sub)})
                    embed = Embed(description=f"**{self.sub} has been deleted from the DB {self.db_type}**", color=0x8B0000)
                    await ctx.response.send_message(embed=embed)
                    self.Value = True
                    return True
                else:
                    await ctx.response.send_message(embed=Embed(
                        color=0x8B0000,
                        title="Sub was not found to have badwords!"
                    ))
                    self.Value = True
                    return True
            if self.db_type == "tied up":
                result = db.tieup.find_one({"guild": ctx.guild.id, "sub": int(self.sub)})
                if result:
                    db.tieup.delete_many({"guild": ctx.guild.id, "sub": int(self.sub)})
                    embed = Embed(description=f"**{self.sub} has been deleted from the DB {self.db_type}**", color=0x8B0000)
                    await ctx.response.send_message(embed=embed)
                    self.Value = True
                    return True
                else:
                    await ctx.response.send_message(embed=Embed(
                        color=0x8B0000,
                        title="Sub was not found to be tied up!"
                    ))
                    self.Value = True
                    return True
        else:
            await ctx.response.send_message(embed=Embed(title="You are not authorized.", color=0x8B0000), ephemeral=True)
            self.Value = True
            return True
    @button(style=ButtonStyle.green, emoji="<:no:1139098428715040768>", custom_id="n", label="NO")
    async def no_button(self, button: Button, ctx: Interaction):
        self.Value = True
        await ctx.response.send_message(embed=Embed(
            color=0x8B0000,
            title="Reset cancelled!, Administrator selected no."
        ))
def setup(client):
    client.add_cog(moderation(client))
