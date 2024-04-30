import discord
from discord.ext import commands
from discord.ui import Button, View
import requests
import time

def get_token():
    url = "https://api.gx.me/profile/token"
    headers = {
        'accept':
        'application/json',
        'accept-language':
        'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'authority':
        'api.gx.me',
        'cookie':
        'SESSION_TYPE=user; SESSION=NzFjMjg3NDAtMDhkOC00ODkwLWJhNzEtODA0YTcwMjNiM2U0',
        'origin':
        'https://www.opera.com',
        'referer':
        'https://www.opera.com/',
        'sec-ch-ua':
        '"Not A(Brand";v="99", "Opera GX";v="107", "Chromium";v="121"',
        'sec-ch-ua-mobile':
        '?0',
        'sec-ch-ua-platform':
        '"Windows"',
        'sec-fetch-dest':
        'empty',
        'sec-fetch-mode':
        'cors',
        'sec-fetch-site':
        'cross-site',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data['data']
    else:
        print("failed")
        return None

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="info", help='shows info about an user')
    async def info(self, ctx, user: discord.Member = None):
        if user is None:
            user = ctx.author
        if user not in ctx.guild.members:
            await ctx.send(f"sorry, but i couldn't find {user.name}")
            return
        game = user.activity.name if user.activity else "Not Active"
        roles = [role.name for role in user.roles]
        embed = discord.Embed(title=f"Infos about {user.display_name}", color=user.color)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="🏷 Username", value=user.name, inline=True)
        embed.add_field(name="🚥 Status", value=user.status.value.title(), inline=True)
        embed.add_field(name="🕹 Activity", value=game, inline=True)
        embed.add_field(name="📆 Created on", value=user.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📆 Joined on", value=user.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🎫 User ID", value=user.id, inline=True)
        if roles:
            embed.add_field(name="🎨 Roles", value=", ".join(roles), inline=False)
        else:
            embed.add_field(name="🎨 Roles", value="None", inline=False)
        if user.bot:
            embed.add_field(name="🤖 Is Bot?", value="Yes", inline=True)
        else:
            embed.add_field(name="🤖 Is Bot?", value="No", inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="clear", help='clears a specified amount of messages')
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("please enter a valid amount of messages!")
            return
        deleted = 0
        while amount > 0:
            delete_count = min(amount, 100)
            messages = await ctx.channel.purge(limit=delete_count + 1)
            deleted += len(messages) - 1
            amount -= delete_count
        await ctx.send(f"total messages cleared: {deleted}")
        
    @commands.command(name="nitro", help='generates a free nitro link (needs payment method)')
    async def nitro(self, ctx):
        token = get_token()
        if token:
            await ctx.send(f"https://discord.com/billing/partner-promotions/1180231712274387115/{token}")
        

async def setup(bot):
    await bot.add_cog(Utils(bot))