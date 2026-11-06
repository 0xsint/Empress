import nextcord
from nextcord import *
from dotenv import load_dotenv
import os
from requests import post, get, patch, delete
from nextcord.ext import commands
import pymongo
import random
import asyncio
load_dotenv()
mongodb = pymongo.MongoClient(os.getenv("MONGODB"))
db = mongodb.femdom_cage
class economy(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @nextcord.slash_command(
        name="bet",
        description="Bet server currency to win"
    )
    async def bet(self, ctx: Interaction, amount: int = SlashOption(name="amount", required=True, description="Amount to bet")):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            currency = db.currency.find_one({"guild": ctx.guild.id})
            currency = currency['result']
            balance = 0
            result = db.balance.find_one({"user": ctx.user.id, "guild": ctx.guild.id})
            try:
                result_i = db.bet_sleeps.find_one({"member": ctx.user.id, "type": "slots"})
                if result_i:
                    await ctx.response.send_message(embed=Embed(title="Cooldown", color=int(c, 0), description=f"Uh oh you're on cooldown! Please wait ``{result['seconds']} seconds``!"))
                    return
                if str(amount) == "all":
                    balance += result['balance']
                if "-" in str(amount):
                    await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't bet with negatives!", color=int(c, 0)))
                    return
                elif "+" in str(amount):
                    await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't have this character when betting!", color=int(c, 0)))
                    return
                elif "." in str(amount):
                    await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't play slots with decimals!", color=int(c, 0)))
                elif int(amount) == 0:
                    await ctx.response.send_message(embed=nextcord.Embed(title="Uh oh! You can't play slots with only the amount of 0!", color=0xffb6c1))
                    return
                elif amount != "all":
                    balance += int(amount)
                if int(result['balance']) < int(balance):
                    await ctx.response.send_message(embed=Embed(description=f"You don't have enough {currency}!", color=int(c, 0)))
                    return
                winorlose = ["❌","✅"]
                choi = random.choices(winorlose, k=3)
                win = 0
                lose = 0
                string = ""
                for res in choi:
                    if res == "✅":
                        string += res
                        win += 1
                    elif res == "❌":
                        string += res
                        lose += 1
                msg = await ctx.response.send_message(embed=Embed(description="***You play slots and land on...<a:prison_loading:1138685852550172703><a:prison_loading:1138685852550172703><a:prison_loading:1138685852550172703>***", color=int(c, 0)))
                await asyncio.sleep(3)
                embed = nextcord.Embed(description=f"***Slots to earn {balance} {currency} {string}***", color=int(c, 0))
                bet = 0
                print (bet)
                R = None
                W = False
                if win == 0:
                    bet -= amount
                    R = -bet
                    W = False
                    embed.add_field(name="You lost!", value=f"{amount}  {currency} has been deducted from you!", inline=False)
                if win == 1:
                    bet -= amount
                    R = -bet
                    W = False
                    embed.add_field(name="You lost!", value=f"{amount}  {currency} has been deducted from you!", inline=False)
                if win == 2:
                    bet += amount
                    R = bet
                    W = True
                    embed.add_field(name="You won!", value=f"{bet}  {currency} has been added!")
                if win == 3:
                    bet += int(amount+amount)
                    R = bet
                    W = True
                    embed.add_field(name="You won double!", value=f"{bet}  {currency} has been added!", inline=False)
                print (R)
                if W:
                    db.balance.update_one({"guild": ctx.guild.id, "user": ctx.user.id}, {"$inc": {"balance": R}}, upsert=True)
                elif not W:
                    db.balance.update_one({"guild": ctx.guild.id, "user": ctx.user.id}, {"$inc": {"balance": -R}}, upsert=True)
                result = db.balance.find_one({"guild": ctx.guild.id, "user": ctx.user.id})
                embed.add_field(name=f"Balance", value=f"Your balance is now {result['balance']} {currency}", inline=False)
                await msg.edit(embed=embed)
                db.bet_sleeps.insert_one({"member": ctx.user.id, "type": "slots", "seconds": 10})
                num = 10
                while num != 0:
                    await asyncio.sleep(1)
                    num -= 1
                    db.bet_sleeps.update_one({"member": ctx.user.id, "type": "slots"}, {"$set": {"seconds": num}})
                if num == 0:
                    db.bet_sleeps.delete_many({"member": ctx.user.id, "type": "slots"})            
            except Exception as e:
                print (e)
                pass
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="balance",
        description="Check a user's balance",
    )
    async def balance_check(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to check balance of", required=False)):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            if not user:
                user = ctx.user
            domme_roles = []
            curr = [domme_roles.append(role.id) for role in ctx.user.roles]
            result_d = db.config.find_one({"guild": ctx.guild.id, "key": "submissive"})
            result_domme = db.config.find_one({"guild": ctx.guild.id, "key": "domme"})
            result_s = db.config.find_one({"guild": ctx.guild.id, "key": "switch"})
            balance = db.balance.find_one({"guild": ctx.guild.id, "user": user.id})
            result = db.currency.find_one({"guild": ctx.guild.id})
            if result_d['value'] in domme_roles:
                await ctx.response.send_message(embed=Embed(description=f"**Hey slut, {user.mention}'s balance is {balance['balance']} {result['result']}**", color=int(c, 0)))
                return
            if result_s['value'] in domme_roles:
                await ctx.response.send_message(embed=Embed(description=f"**Hey Goddess/slut, {user.mention}'s balance is {balance['balance']} {result['result']}**", color=int(c, 0)))
                return
            if result_domme['value'] in domme_roles:
                await ctx.response.send_message(embed=Embed(description=f"**Hey Goddess, {user.mention}'s balance is {balance['balance']} {result['result']}**", color=int(c, 0)))
                return
        else:
            await ctx.response.send_message(embed=Embed(
                title="Not configured!",
                description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                color=0xffa4e4
            ))
    @nextcord.slash_command(
        name="give",
        description="Give an amount of server currency"
    )
    async def give_command(self, ctx: Interaction, user: Member = SlashOption(name="user", description="User to give currency to", required=True), amount: int = SlashOption(name="amount", required=True, description="Amount to give")):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            if user == ctx.user:
                await ctx.response.send_message(embed=Embed(title="You can't give money to yourself.", color=int(c, 0)))
                return
            if "-" in str(amount):
                await ctx.response.send_message(embed=Embed(title="Unable to give negative number!",color=int(c, 0)))
                return
            if "+" in str(amount):
                await ctx.response.send_message(title="Unable to give currency with this character.", color=int(c, 0))
            user_bal_q = {"guild": ctx.guild.id, "user": ctx.user.id}
            result = db.balance.find_one(user_bal_q)
            result_a = db.currency.find_one({"guild": ctx.guild.id})
            if int(result['balance']) < int(amount):
                await ctx.response.send_message(embed=Embed(description=f"You don't have enough {result_a['result']}!", color=int(c, 0)))
                return
            db.balance.update_one({"guild": ctx.guild.id, "user": ctx.user.id}, {"$inc": {"balance": -amount}}, upsert=True)
            db.balance.update_one({"guild": ctx.guild.id, "user": user.id}, {"$inc": {"balance": amount}}, upsert=True)
            await ctx.response.send_message(embed=Embed(description=f"**Hey {user.mention}, {ctx.user.mention} has given you a balance of {amount} {result_a['result']}**", color=int(c, 0)))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
    @nextcord.slash_command(
        name="daily",
        description="Collect daily"
    )
    async def daily(self, ctx: Interaction):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            if db.cooldowns.find_one({"member": ctx.user.id, "guild": ctx.guild.id}):
                await ctx.response.send_message(embed=Embed(description=f"**Hey {ctx.user.mention}, You already collected your daily today!**", color=int(c, 0)))
                return
            db.balance.update_one({"guild": ctx.guild.id, "user": ctx.user.id}, {"$inc": {"balance": 200}})
            result_a = db.currency.find_one({"guild": ctx.guild.id})
            await ctx.response.send_message(embed=Embed(description=f"**Hey {ctx.user.mention}, you have been given a balance of 200 {result_a['result']}**", color=int(c, 0)))
            db.cooldowns.insert_one({"member": ctx.user.id, "guild": ctx.guild.id})
            await asyncio.sleep(78000)
            db.cooldowns.delete_many({"member": ctx.user.id, "guild": ctx.guild.id})
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
    @nextcord.slash_command(
        name="buy",
        description="Buy a role from the role shop"
    )
    async def buy(self, ctx: Interaction, id: str = SlashOption(description="id of what to buy", required=True)):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            user_bal_q = {"guild": ctx.guild.id, "user": ctx.user.id}
            result = db.balance.find_one(user_bal_q)
            result_a = db.currency.find_one({"guild": ctx.guild.id})
            r = db.buyable.find_one({"id": id, "guild": ctx.guild.id})
            role = ctx.guild.get_role(r['role'])
            if int(result['balance']) < r['price']:
                await ctx.response.send_message(embed=Embed(description=f"You don't have enough {result_a['result']}!", color=int(c, 0)))
                return
            db.balance.update_one({"guild": ctx.guild.id, "user": ctx.user.id}, {"$inc": {"balance": r['price']}})
            await ctx.user.add_roles(role)
            await ctx.response.send_message(embed=Embed(description=f"**You have purchased {role.mention}!**", color=int(c, 0)))
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
    @nextcord.slash_command(
        name="shop",
        description="Shop list"
    )
    async def get_shop(self, ctx: Interaction):
        if db.options.find_one({"guild": ctx.guild.id, "economy": True}):
            color = db.custom.find_one({"type": "color", "guild": ctx.guild.id})
            c = color['string']
            if "0x" not in c:
                if "#" not in c:
                    c = "0x"+c
                else:
                    c = c.replace("#", "0x")
            embed = Embed(description="**Heres the list of the buyable roles for this server:**\r\n")
            for result in db.buyable.find({"guild": ctx.guild.id}):
                role = ctx.guild.get_role(result['role'])
                
                embed.description += f"* {result['id']} - {result['price']} : {role.mention}\r\n"
            await ctx.response.send_message(embed=embed)
        else:
            await ctx.response.send_message(embed=Embed(
                        title="Not configured!",
                        description=f"This server is not configured for economy, please ask the owner to configure the server using the ``/settings enable`` command",
                        color=0xffa4e4
                    ))
def setup(client):
    client.add_cog(economy(client))
