import nextcord
from nextcord import *
from dotenv import load_dotenv
import os
from nextcord.ext import commands
import pymongo
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class help(commands.Cog):
    def __init__(self, client):
        self.client = client
    @nextcord.slash_command(name="donate", description="Donate to help support the bot!")
    async def donate(self, ctx: Interaction):
        await ctx.response.send_message(embed=Embed(title="Help us!", description=f"Hello, I'm Lina and I want to tell you how you can help us support {self.client.user.name} and keep it online! First off it's 2 easy steps, first you go to our Patreon and donate a measly $3/mo and you unlock all of our donor commands! What are those you may ask? I'm glad you asked! The donor commands currently are ``/edit``, ``/create``, and ``/customize``! That's it! Obviously donating is needed unless you really wanna help the cause. We will not ask for your money unless for these specific commands (This policy is subject ot change). What are you waiting for? [Click here to donate!](https://patreon.com/AlphaShine) For security purposes, our link takes you to ``https://patreon.com/AlphaShine``", color=0xffa4e4).add_field(name="Step 2:", value=f"Navigate to our activation portal using ``/activate``"))
    @nextcord.slash_command(name="activate", description="Activate your donation perks!")
    async def activate(self, ctx: Interaction):
        await ctx.response.send_message(embed=Embed(title="Activation portal", description=f"Assuming you have went to our Patreon and donated already, [Here is your activation link](http://sorceress.online/femdom/patreon_link/{ctx.user.id})! We appreciate you donating and your support will not be forgotten!", color=0xffa4e4), ephemeral=True)
    @nextcord.slash_command(
        name="commands",
        description="Slash commands for the bot"
    )
    async def command(self, ctx: Interaction, category: Literal["SAFEWORD","BDSM","Porn","Donate","Invite","Roleplay","Levels", "Economy", "Moderation", "Admin", "Feedback"] = SlashOption(description="Choose a category", required=True)):
        com = []
        if category.upper() == "SAFEWORD":
            await ctx.response.send_message(embed=Embed(
                title="Safeword", description="* **To activate the safeword, please use ``/safeword``!**",
                color=0x8B0000
            ))
        if category.upper() == "BDSM":
            await ctx.response.send_message(
                embed=Embed(title="BDSM Commands", description=f"* Give a sub a task - ``/task give``\r\n* Remove a Task by given Task ID - ``/task completed``\r\n* List a current sub's tasks - ``/task list``\r\n* Prison lock - ``/prison lock``\r\n* Prison Unlock - ``/prison unlock``\r\n* Ownership Status - ``/status``\r\n* Own a sub - ``/own``\r\n* Disown a sub - ``/disown``\r\n* Gag a sub - ``/gag``\r\n* Tie up a sub - ``/tie bind``\r\n* Untie a sub - ``/tie untie``\r\n* Add a badword - ``/badword add``\r\n* Clear all badwords - ``/badword clear``\r\n* Remove a badword - ``/badword remove``\r\n* Say a message as a claimed sub - ``/say``\r\n* Get a list of gagged subs - ``/gagged``\r\n* Get a list of locked subs - ``/locked``\r\n* Get a list of badworded subs - ``/badword list``\r\n* Get a list of tied up subs - ``/tie list``\r\n* Check a user's profile - ``/profile``\r\n* Create your profile - ``/create``\r\n* Edit your profile - ``/edit``\r\n* Add blindfold to sub - ``/blindfold add member``\r\n* Add blindfold channel spectator - ``/blindfold add spectator``\r\n* Remove blindfold off sub - ``/blindfold remove member``\r\n* Remove spectator from blindfold channel - ``/blindfold remove spectator``", color=0X8b0000)
            )
            return
        if category.upper() == "DONATE":
            await ctx.response.send_message(
                embed=Embed(title="Donate Commands", description="* Donate! - ``/donate``\r\n* Activate your donation - ``/activate``", color=0xffa4e4)
            )
            return
        if category.upper() == "INVITE":
            await ctx.response.send_message(
                embed=Embed(title="Invite Command", description="* Get a bot invite - ``/invite``", color=0xffa4e4)
            )
            return
        """if category.upper() == "PORN":
            await ctx.response.send_message(
                embed=Embed(title="Porn Commands", description="* Porn search - ``/porn search``", color=0xffa4e4)
            )
            return"""
        if category.upper() == "ROLEPLAY":
            await ctx.response.send_message(
                embed=Embed(title="RP Commands", description="* Bite - ``/roleplay bite``\r\n* Hug - ``/roleplay hug``\r\n* Kiss - ``/roleplay kiss``\r\n* Cuddle - ``/roleplay cuddle``\r\n* Pet - ``/roleplay pet``\r\n* Slap - ``/roleplay slap``\r\n* Poke - ``/roleplay poke\``r\n* Blush - ``/roleplay blush``\r\n* Wag - ``/roleplay wag``\r\n* Purr - ``/roleplay purr``\r\n* Cry - ``/roleplay cry``\r\n* Pout - ``/roleplay pout``\r\n* Boop - ``/roleplay boop``\r\n* Tickle - ``/roleplay tickle``\r\n* Fuck - ``/nsfw_rp fuck``\r\n Peg - ``/nsfw_rp peg``\r\n* Whip - ``/nsfw_rp whip``\r\n* Tie up - ``/nsfw_rp tie_up``\r\n* Gag - ``/nsfw_rp gag``\r\n* Worship - ``/nsfw_rp worship``\r\n*", color=0x8B0000)
            )
        if category.upper() == "LEVELS":
            await ctx.response.send_message(
                embed=Embed(title="Level Commands", description="* Check level - ``/level``", color=0xffa4e4)
            )
            return
        if category.upper() == "ECONOMY":
            await ctx.response.send_message(
                embed=Embed(title="Economy Commands", description="* Check Balance - /balance\r\n* Play Slots - ``/bet``\r\n* Collect Daily - ``/daily``\r\n* Give currency - ``/give``\r\n* List items in the shop - /shop\r\n* Buy a role - ``/buy``", color=0X8b0000)
            )
            return
        if category.upper() == "MODERATION":
            await ctx.response.send_message(
                embed=Embed(title="Moderation Commands", description="* Set level - ``/set level``\r\n* Override gag - ``/force_ungag``\r\n* Override Badwords - ``/force_badword``\r\n* Override bondage - ``/force_untie``\r\n* Override Prison - ``/force_unlock``\r\n* Reset ownership - ``/reset``\r\n* Remove a sub from the listing database - ``/delete_from_db``\r\n* Force remove blindfold - ``/force_remove_blindfold``", color=0x8B0000)
            )
            return
        if category.upper() == "ADMIN":
            await ctx.response.send_message(
                embed=Embed(title="Admin Commands", description="* Customize your server - ``/customize``\r\n* Set server currency - ``/currency``\r\n* Update a buyable role - ``/update_buyable_role``\r\n* Delete buyable role - ``/delete_buyable_role``\r\n* Configure your server for BDSM commands - ``/config bdsm``\r\n* Settings to configure your server to your liking - ``/settings enable`` and ``/settings disable``\r\n* To set a punishments channel and/or level channel, gag logs channel ``/set channel``\r\n* Set permissions of who can use the prison commands - ``/permissions``", color=0x8B0000)
            )
            return
        if category.upper() == "FEEDBACK":
            await ctx.response.send_message(
                embed=Embed(title="Feedback Command", description="* Submit feedback, Bug report, Account Data Deletion or Rating - ``/feedback``", color=0X8b0000)
            )
            return
    @nextcord.slash_command(
        name="help",
        description="Slash commands for the bot"
    )
    async def commandH(self, ctx: Interaction, category: Literal["SAFEWORD","BDSM","Porn","Donate","Invite","Roleplay","Levels", "Economy", "Moderation", "Admin", "Feedback"] = SlashOption(description="Choose a category", required=True)):
        com = []
        if category.upper() == "SAFEWORD":
            await ctx.response.send_message(embed=Embed(
                title="Safeword", description="* **To activate the safeword, please use ``/safeword``!**",
                color=0x8B0000
            ))
        if category.upper() == "BDSM":
            await ctx.response.send_message(
                embed=Embed(title="BDSM Commands", description=f"* Give a sub a task - ``/task give``\r\n* Remove a Task by given Task ID - ``/task completed``\r\n* List a current sub's tasks - ``/task list``\r\n* Prison lock - ``/prison lock``\r\n* Prison Unlock - ``/prison unlock``\r\n* Ownership Status - ``/status``\r\n* Own a sub - ``/own``\r\n* Disown a sub - ``/disown``\r\n* Gag a sub - ``/gag``\r\n* Tie up a sub - ``/tie bind``\r\n* Untie a sub - ``/tie untie``\r\n* Add a badword - ``/badword add``\r\n* Clear all badwords - ``/badword clear``\r\n* Remove a badword - ``/badword remove``\r\n* Say a message as a claimed sub - ``/say``\r\n* Get a list of gagged subs - ``/gagged``\r\n* Get a list of locked subs - ``/locked``\r\n* Get a list of badworded subs - ``/badword list``\r\n* Get a list of tied up subs - ``/tie list``\r\n* Check a user's profile - ``/profile``\r\n* Create your profile - ``/create``\r\n* Edit your profile - ``/edit``\r\n* Add blindfold to sub - ``/blindfold add member``\r\n* Add blindfold channel spectator - ``/blindfold add spectator``\r\n* Remove blindfold off sub - ``/blindfold remove member``\r\n* Remove spectator from blindfold channel - ``/blindfold remove spectator``", color=0X8b0000)
            )
            return
        if category.upper() == "DONATE":
            await ctx.response.send_message(
                embed=Embed(title="Donate Commands", description="* Donate! - ``/donate``\r\n* Activate your donation - ``/activate``", color=0xffa4e4)
            )
            return
        if category.upper() == "INVITE":
            await ctx.response.send_message(
                embed=Embed(title="Invite Command", description="* Get a bot invite - ``/invite``", color=0xffa4e4)
            )
            return
        """if category.upper() == "PORN":
            await ctx.response.send_message(
                embed=Embed(title="Porn Commands", description="* Porn search - ``/porn search``", color=0xffa4e4)
            )
            return"""
        if category.upper() == "ROLEPLAY":
            await ctx.response.send_message(
                embed=Embed(title="RP Commands", description="* Bite - ``/roleplay bite``\r\n* Hug - ``/roleplay hug``\r\n* Kiss - ``/roleplay kiss``\r\n* Cuddle - ``/roleplay cuddle``\r\n* Pet - ``/roleplay pet``\r\n* Slap - ``/roleplay slap``\r\n* Poke - ``/roleplay poke\``r\n* Blush - ``/roleplay blush``\r\n* Wag - ``/roleplay wag``\r\n* Purr - ``/roleplay purr``\r\n* Cry - ``/roleplay cry``\r\n* Pout - ``/roleplay pout``\r\n* Boop - ``/roleplay boop``\r\n* Tickle - ``/roleplay tickle``\r\n* Fuck - ``/nsfw_rp fuck``\r\n Peg - ``/nsfw_rp peg``\r\n* Whip - ``/nsfw_rp whip``\r\n* Tie up - ``/nsfw_rp tie_up``\r\n* Gag - ``/nsfw_rp gag``\r\n* Worship - ``/nsfw_rp worship``\r\n*", color=0x8B0000)
            )
        if category.upper() == "LEVELS":
            await ctx.response.send_message(
                embed=Embed(title="Level Commands", description="* Check level - ``/level``", color=0xffa4e4)
            )
            return
        if category.upper() == "ECONOMY":
            await ctx.response.send_message(
                embed=Embed(title="Economy Commands", description="* Check Balance - /balance\r\n* Play Slots - ``/bet``\r\n* Collect Daily - ``/daily``\r\n* Give currency - ``/give``\r\n* List items in the shop - /shop\r\n* Buy a role - ``/buy``", color=0X8b0000)
            )
            return
        if category.upper() == "MODERATION":
            await ctx.response.send_message(
                embed=Embed(title="Moderation Commands", description="* Set level - ``/set level``\r\n* Override gag - ``/force_ungag``\r\n* Override Badwords - ``/force_badword``\r\n* Override bondage - ``/force_untie``\r\n* Override Prison - ``/force_unlock``\r\n* Reset ownership - ``/reset``\r\n* Remove a sub from the listing database - ``/delete_from_db``\r\n* Force remove blindfold - ``/force_remove_blindfold``", color=0x8B0000)
            )
            return
        if category.upper() == "ADMIN":
            await ctx.response.send_message(
                embed=Embed(title="Admin Commands", description="* Set server currency - ``/currency``\r\n* Update a buyable role - ``/update_buyable_role``\r\n* Delete buyable role - ``/delete_buyable_role``\r\n* Configure your server for BDSM commands - ``/config bdsm``\r\n* Settings to configure your server to your liking - ``/settings enable`` and ``/settings disable``\r\n* To set a punishments channel and/or level channel, gag logs channel ``/set channel``\r\n* Set permissions of who can use the prison commands - ``/permissions``", color=0x8B0000)
            )
            return
        if category.upper() == "FEEDBACK":
            await ctx.response.send_message(
                embed=Embed(title="Feedback Command", description="* Submit feedback, Bug report, Account Data Deletion or Rating - ``/feedback``", color=0X8b0000)
            )
            return
def setup(client):
    client.add_cog(help(client))
