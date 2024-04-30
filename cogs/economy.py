import asyncio
import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random

def create_embed(title, description, color=discord.Color.gold()):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

def generate_math_question():
    operators = ['+', '-', '*']
    operator = random.choice(operators)
    if operator == '+':
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        question = f"What is {num1} {operator} {num2}?"
        answer = num1 + num2
    elif operator == '-':
        num1 = random.randint(1, 100)
        num2 = random.randint(1, num1)
        question = f"What is {num1} {operator} {num2}?"
        answer = num1 - num2
    else:
        num1 = random.randint(1, 20)
        num2 = random.randint(1, 10)
        question = f"What is {num1} {operator} {num2}?"
        answer = num1 * num2
    return question, answer

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='balance', help='check your balance')
    async def balance(self, ctx):
        user_id = str(ctx.author.id)
        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_data = balances.get(user_id, {'balance': 0, 'last_daily': None, 'last_work': None})
        embed = create_embed("balance", f'you currently have {user_data["balance"]} coins')
        await ctx.send(embed=embed)

    @commands.command(name='send', help='send someone money')
    async def send(self, ctx, amount: int, user: discord.User):
        author_id = str(ctx.author.id)
        user_id = str(user.id)
        if amount <= 0:
            embed = create_embed("error", "please enter a valid amount of coins")
            await ctx.send(embed=embed)
            return
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if author_id not in balances or balances[author_id]['balance'] < amount:
            embed = create_embed("error", "you don't have enough coins")
            await ctx.send(embed=embed)
        else:
            balances[author_id]["balance"] -= amount
            balances[user_id] = balances.get(user_id, {'balance': 0})
            balances[user_id]["balance"] += amount
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            embed = create_embed("success", f'successfully sent {amount} coins to {user.name}')
            await ctx.send(embed=embed)

    @commands.command(name='work', help='work to earn coins')
    async def work(self, ctx):
        user_id = str(ctx.author.id)
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if user_id not in balances:
            balances[user_id] = {'balance': 0, 'last_daily': None, 'last_work': None}
        if "last_work" not in balances[user_id] or balances[user_id]["last_work"] != user_id:
            question, answer = generate_math_question()
            embed = create_embed("work", question)
            message = await ctx.send(embed=embed)
            def check(msg):
                return msg.author == ctx.author and msg.channel == ctx.channel
            try:
                user_answer_msg = await self.bot.wait_for('message', timeout=15, check=check)
            except asyncio.TimeoutError:
                await ctx.send("time is up! you didn't answer in time")
                return
            try:
                user_answer = int(user_answer_msg.content)
            except ValueError:
                await ctx.send("wrong! work cancelled")
                return
            if user_answer == answer:
                earned_coins = random.randint(20, 50)
                balances[user_id]["balance"] += earned_coins
                balances[user_id]["last_work"] = user_id
                with open("balances.json", "w") as f:
                    json.dump(balances, f)
                embed = create_embed("work", f'correct! you earned {earned_coins} coins')
            else:
                embed = create_embed("work", "wrong! work cancelled")
            await message.edit(embed=embed)
        else:
            embed = create_embed("error", "you can only work once per hour")
            await ctx.send(embed=embed)

    @commands.command(name='daily', help='claim your daily coins')
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if user_id not in balances:
            balances[user_id] = {'balance': 0, 'last_daily': None, 'last_work': None}
        if "last_daily" not in balances[user_id] or balances[user_id]["last_daily"] != user_id:
            daily_reward = 100
            balances[user_id]["balance"] += daily_reward
            balances[user_id]["last_daily"] = user_id
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            embed = create_embed("daily", f'you claimed your {daily_reward} daily coins')
            await ctx.send(embed=embed)
        else:
            embed = create_embed("error", "you can only claim your daily coins once per day")
            await ctx.send(embed=embed)

    @commands.command(name='casino', help='play casino')
    async def casino(self, ctx, bet_amount: int = None):
        user_id = str(ctx.author.id)
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if user_id not in balances:
            balances[user_id] = {'balance': 0, 'last_daily': None, 'last_work': None}
        if balances[user_id]['balance'] == 0:
            embed = create_embed("error", "you don't have any coins to play casino")
            await ctx.send(embed=embed)
        else:
            if bet_amount is None:
                bet_amount = max(balances[user_id]['balance'] // 2, 1)  # Set default bet to half of the balance
            if bet_amount > balances[user_id]['balance']:
                embed = create_embed("error", "you're too broke to play casino")
                await ctx.send(embed=embed)
            else:
                embed = create_embed("casino", f"do you want to play casino with a bet of {bet_amount} coins?")
                message = await ctx.send(embed=embed)
                await message.add_reaction('✅')
                await message.add_reaction('❌')
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == message.id
                try:
                    reaction, _ = await self.bot.wait_for('reaction_add', timeout=30, check=check)
                except TimeoutError:
                    embed = create_embed("casino", "you took too long to respond. casino cancelled")
                    await message.edit(embed=embed)
                else:
                    if str(reaction.emoji) == '✅':
                        outcome = random.choice(["win", "lose"])
                        if outcome == "win":
                            balances[user_id]["balance"] += bet_amount
                            result_embed = create_embed("result", f'congratulations! you won {bet_amount} coins')
                        else:
                            balances[user_id]["balance"] -= bet_amount
                            result_embed = create_embed("result", f'rip! you lost {bet_amount} coins')
                        with open("balances.json", "w") as f:
                            json.dump(balances, f)
                        await message.edit(embed=result_embed)
                    else:
                        embed = create_embed("casino", "casino cancelled")
                        await message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))