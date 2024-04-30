import chat_exporter
import discord
from discord.ext import commands
from discord.ui import Button, button, View
import asyncio
import datetime
import uuid
import os
from github import Github
import json

async def send_log(title: str, description: str, color: discord.Color, guild: discord.Guild, log_channel_id: int):
    log_channel = guild.get_channel(log_channel_id)
    embed = discord.Embed(title=title, description=description, color=color)
    await log_channel.send(embed=embed)
    
async def get_transcript(member: discord.Member, channel: discord.TextChannel):
    export = await chat_exporter.export(channel=channel)
    file_name = f"{member.id}.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(export)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.get_config()

    def get_config(self):
        with open('config.json', 'r') as file:
            return json.load(file)

    def upload(self, file_path: str, member_name: str):
        github_token = self.config['github_token']
        repo_name = self.config['repo_name']
        github_username = self.config['github_username']
        g = Github(github_token)
        repo = g.get_user(github_username).get_repo(repo_name)
        current_time = int(time.time())
        file_name = str(uuid.uuid4()) + ".html"
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            repo.create_file(file_name, f"Added transcript for {member_name}", content)
        netlify_link = f"https://transcripts69.netlify.app/{file_name}"
        os.remove(file_path)
        return netlify_link
        
    class TicketButton(View):
        def __init__(self, category_id, role_id, emoji, ticket_type, log_channel_id):
            super().__init__(timeout=None)
            self.category_id = category_id
            self.role_id = role_id
            self.emoji = emoji
            self.ticket_type = ticket_type
            self.log_channel_id = log_channel_id

        @button(label="ticket", style=discord.ButtonStyle.blurple, emoji="🛒", custom_id="ticketopen")
        async def ticket(self, interaction: discord.Interaction, button: Button):
            await interaction.response.defer(ephemeral=True)
            category = discord.utils.get(interaction.guild.categories, id=self.category_id)
            for ch in category.text_channels:
                if ch.topic == f"{interaction.user.id}":
                    await interaction.followup.send(f"you already have a ticket: {ch.mention}", ephemeral=True)
                    return
            r1 = interaction.guild.get_role(self.role_id)
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            channel = await category.create_text_channel(
                name=str(interaction.user),
                topic=f"{interaction.user.id}",
                overwrites=overwrites
            )
            
            description_text = ""
            if self.ticket_type == "support":
                description_text = "please tell us about your problem."
            elif self.ticket_type == "order":
                description_text = "please tell us what you'd like to buy."

            await channel.send(
                embed=discord.Embed(title="ticket created", description=description_text, color=discord.Color.green()),
                view=self.CloseButton(category_id=self.category_id, role_id=self.role_id, ticket_type=self.ticket_type, log_channel_id=self.log_channel_id)
            )
            
            await interaction.followup.send(
                embed=discord.Embed(description=f"{channel.mention}", color=discord.Color.blurple()),
                ephemeral=True
            )
            
            await send_log(title="ticket created", description=f"{interaction.user.mention}", color=discord.Color.green(), guild=interaction.guild, log_channel_id=self.log_channel_id)

        class CloseButton(View):
            def __init__(self, category_id, role_id, ticket_type, log_channel_id):
                super().__init__(timeout=None)
                self.category_id = category_id
                self.role_id = role_id
                self.ticket_type = ticket_type
                self.log_channel_id = log_channel_id

            @button(label="close", style=discord.ButtonStyle.red, custom_id="closeticket", emoji="🔒")
            async def close(self, interaction: discord.Interaction, button: Button):
                await interaction.response.defer(ephemeral=True)
                await interaction.channel.send("closing in 3s...")
                await asyncio.sleep(3)
                category = discord.utils.get(interaction.guild.categories, id=self.category_id)
                r1 = interaction.guild.get_role(self.role_id)
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    r1: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                await interaction.channel.edit(category=category, overwrites=overwrites)
                await interaction.channel.send(
                    embed=discord.Embed(description="ticket closed", color=discord.Color.red()),
                    view=self.TrashButton(category_id=self.category_id, ticket_type=self.ticket_type, log_channel_id=self.log_channel_id)
                )
                member = interaction.guild.get_member(int(interaction.channel.topic.split(" ")[0]))
                await get_transcript(member=member, channel=interaction.channel)
                file_name = self.upload(f'{member.id}.html', member.name)
                await send_log(title="ticket closed", description=f"closed by {interaction.user.mention}\n[open transcript]({file_name})", color=discord.Color.yellow(), guild=interaction.guild, log_channel_id=self.log_channel_id)

            class TrashButton(View):
                def __init__(self, category_id, ticket_type, log_channel_id):
                    super().__init__(timeout=None)
                    self.category_id = category_id
                    self.ticket_type = ticket_type
                    self.log_channel_id = log_channel_id

                @button(label="delete", style=discord.ButtonStyle.red, emoji="❌", custom_id="trash")
                async def trash(self, interaction: discord.Interaction, button: Button):
                    await interaction.response.defer()
                    await interaction.channel.send("deleting in 3s...")
                    await asyncio.sleep(3)
                    await interaction.channel.delete()
                    await send_log(title="ticket deleted", description=f"deleted by {interaction.user.mention}, ticket: {interaction.channel.name}", color=discord.Color.red(), guild=interaction.guild, log_channel_id=self.log_channel_id)

    @commands.command(name="order", brief='sends an order ticket creator', description='sends a message to open an order ticket')
    @commands.has_permissions(administrator=True)
    async def order(self, ctx, category_id: int, log_channel_id: int, role_id: int):
        await ctx.send(embed=discord.Embed(description="click on the button to order something!"), view=self.TicketButton(
            category_id=category_id,
            role_id=role_id,
            emoji="🛒",
            ticket_type="order",
            log_channel_id=log_channel_id
        ))

    @commands.command(name="support", brief='sends a support ticket creator', description='sends a message to open a support ticket')
    @commands.has_permissions(administrator=True)
    async def support(self, ctx, category_id: int, log_channel_id: int, role_id: int):
        await ctx.send(embed=discord.Embed(description="click on the button to create a support ticket!"), view=self.TicketButton(
            category_id=category_id,
            role_id=role_id,
            emoji="🎫",
            ticket_type="support",
            log_channel_id=log_channel_id
        ))

async def setup(bot):
    await bot.add_cog(Ticket(bot))
