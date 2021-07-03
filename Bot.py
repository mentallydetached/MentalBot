#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !pip install discord
# !pip uninstall jthon


# In[1]:


# Import Stack
import discord
import jthon
from discord.ext import commands
from pathlib import Path
import os
from discord.ext.commands import has_permissions
from discord.utils import get
import discord.abc


# In[8]:



class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color(0x57F287), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

# Variable Defs
help_command = commands.DefaultHelpCommand(no_category = 'Other Commands')
config = jthon.load('config')
token = str(config.get("token")) #pulls the bot token from the hidden config file
bot = commands.Bot(
    command_prefix = commands.when_mentioned_or('!'),
    description = "A simple bot designed to annoy people.",
    help_command = None
)
bot.help_command = MyHelpCommand()

# Function Defs
def automatic_cog_load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')

#Bot Events
@bot.event
async def on_ready():
    print("Bot is operational!")

@bot.event 
async def on_command_error(ctx, error):
    e = discord.Embed(colour=discord.Colour(0xED4245), description=f"{error}")
    await ctx.send(embed=e)

#Bot Commands
@commands.is_owner()
@bot.command()
async def shutdown(ctx):
    """Allows the owner of the bot to shut down the bot from within Discord."""
    e = discord.Embed(colour=discord.Colour(0x57F287), description="Command Received, Shutting down Bot!")
    await ctx.send(embed=e)
    exit()

automatic_cog_load()

bot.run(token)


# In[ ]:




