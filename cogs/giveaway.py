import asyncio
import discord
import datetime
from discord.ext import commands
from discord.ui import Button, View

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_permissions(administrator=True)
    @commands.command(name="giveaway", help='creates a giveaway with the specified arguments')
    async def start_giveaway(self, ctx, item, winners: int, duration):
        duration_seconds = self.convert_to_seconds(duration)
        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=duration_seconds)
        
        embed = discord.Embed(title=f"__{item}__", description=f"react to enter the giveaway!\nends <t:{int(end_time.timestamp())}:R>", color=0x00ff00)
        embed.add_field(name="winners", value=winners, inline=True)
        embed.set_footer(text=f"hosted by {ctx.author.display_name}")
        
        giveaway_msg = await ctx.send(embed=embed)
        await giveaway_msg.add_reaction("🎉")
        await asyncio.sleep(duration_seconds)
        giveaway_msg = await ctx.fetch_message(giveaway_msg.id)
        
        participants = [user for reaction in giveaway_msg.reactions if str(reaction.emoji) == "🎉" async for user in reaction.users() if user != self.bot.user]
        
        if len(participants) >= winners:
            chosen_winners = random.sample(participants, winners)
            winner_mentions = ", ".join([winner.mention for winner in chosen_winners])
            await ctx.send(f"# 🎉 congratulations {winner_mentions}! you won {item}.")
        else:
            await ctx.send("not enough participants. cancelling giveaway...")
            
    def convert_to_seconds(self, duration):
        unit_multiplier = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
        unit = duration[-1]
        return int(duration[:-1]) * unit_multiplier.get(unit, 1)

async def setup(bot):
    await bot.add_cog(Giveaway(bot))