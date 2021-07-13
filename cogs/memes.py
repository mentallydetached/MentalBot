from discord.ext import commands
import random
import discord
import os

memePics = []
for filename in os.listdir('cogs/memes'):
    memePics.append(f'cogs/memes/{filename}')


class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["m", "randommeme", "random_meme", "meme"])
    async def memes(self, ctx):
        """Fulfills your life with a random meme."""
        await ctx.send(file=discord.File(random.choice(memePics)))


def setup(bot):
    bot.add_cog(Images(bot))
