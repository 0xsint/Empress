import nextcord
from nextcord import *
from dotenv import load_dotenv
import os
from nextcord.ext import application_checks
from nextcord.ext import commands
import nextcord.utils
import nextcord
import pymongo
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class levels(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
    @nextcord.slash_command(name="level", description="Check a level of a user")
    async def level(self, ctx: Interaction, user: Member = SlashOption(required=False, name="user", description="User to check level of")):
        if db.options.find_one({"guild": ctx.guild.id, "levels": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            if not user:
                user = ctx.user
            result = db.levels.find_one({"member": user.id, "guild": ctx.guild.id})
            if not result:
                await ctx.response.send_message(embed=Embed(title="Unable to find level of user.", color=0xdea5a4))
                return
            exp = int(result['exp'])
            level = int(result['level'])
            math =round(exp//100)
            bar = None
            if math < 10:
                bar = "[----------]"
            elif math >= 10:
                bar = "[ღ---------]"
            elif math >= 20:
                bar = "[ღღ--------]"
            elif math >= 30:
                bar = "[ღღღ-------]"
            elif math >= 40:
                bar = "[ღღღღ------]"
            elif math >= 50:
                bar = "[ღღღღღ-----]"
            elif math >= 60:
                bar = "[ღღღღღღ----]"
            elif math >= 70:
                bar = "[ღღღღღღღ---]"
            elif math >= 80:
                bar = "[ღღღღღღღღ--]"
            elif math >= 90:
                bar = "[ღღღღღღღღღ-]"
            elif math >= 100:
                bar = "[ღღღღღღღღღღ]"
            roles = ctx.user.roles
            sub = True
            domme = False
            switch = False
            await ctx.response.send_message(embed=nextcord.Embed(description=f"**Hey {ctx.user.mention}! {user.mention}'s level is ``{level}``**\r\n **with a total amount of XP earned: ``{exp}`` XP.**", color=int(c, 0)))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for levels, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
    @nextcord.slash_command(name="level_", description="Administrator", default_member_permissions=Permissions(manage_guild=True))
    async def level_(self, ctx: Interaction):
        pass
    @application_checks.has_guild_permissions(manage_guild=True)
    @level_.subcommand(name="reward", description="Level rewarding")
    async def reward(self, ctx: Interaction, level: int = SlashOption(name="level", description="Level to get reward", required=True), reward: Role = SlashOption(required=True, description="Role to reward")):
        if db.options.find_one({"guild": ctx.guild.id, "levels": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            db.levels_reward.insert_one({"role": reward.id, "level": level, "guild": ctx.guild.id})
            await ctx.response.send_message(embed=Embed(title=f"Level Reward for {level}", description=f"Level {level} will now grant the role {reward.mention}", color=int(c, 0)), ephemeral=True)
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for levels, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
    
    @nextcord.slash_command(name="delete", description="Delete function", default_member_permissions=Permissions(manage_guild=True))
    @application_checks.has_guild_permissions(manage_guild=True)
    async def delete(self, ctx: Interaction):
        pass
    @delete.subcommand(name="reward", description="Delete a level reward")
    @application_checks.has_guild_permissions(manage_guild=True)
    async def del_reward(self, ctx: Interaction, role: str = SlashOption(name="role_id", description="Role ID to delete", required=True), level: int = SlashOption(name="level", description="Level unlocked", required=False)):
        if db.options.find_one({"guild": ctx.guild.id, "levels": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            result = db.levels_reward.find_one_and_delete({"$or": [{"guild": ctx.guild.id, "role": int(role)}, {"guild": ctx.guild.id, "role": int(role), "level": level}]})
            await ctx.response.send_message(embed=Embed(title=f"Role ID {role}", description=f"Role ID {role} will no longer be unlocked at level {level}", color=int(c, 0)).set_footer(text="DELETE"), ephemeral=True)
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for levels, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
def setup(client):
    client.add_cog(levels(client))
