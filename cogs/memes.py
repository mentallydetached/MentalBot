from discord.ext import commands
import random
import discord
import os
from simpletransformers.t5 import T5Model
import sys
import logging

model_args = {
    "use_cuda": False,
    "silent": True,
}

model = T5Model(
    "t5",
    "t5-base",
    use_cuda=False, 
    args=model_args
)

memePics = []
for filename in os.listdir('cogs/memes'):
    memePics.append(f'cogs/memes/{filename}')

    
def checkSentenceMatch(sentence1, sentence2):
    match_rate = model.predict([f"stsb sentence1: {sentence1} sentence2: {sentence2}"])[0]
    match_percent = ((float(match_rate) * 100) / 5)
    return match_percent
    
class images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
#     @commands.has_role("Staff")
    @commands.command(aliases=["m","randommeme","random_meme","memes"])
    async def meme(self, ctx):
        """Fulfills your life with a random meme."""
        await ctx.send(file=discord.File(random.choice(memePics)))
        
#     @commands.has_role("Staff")
    @commands.command(hidden=True)
    async def simpforcat(self, ctx):
        await ctx.send(file=discord.File(random.choice(catPics)))


    @commands.Cog.listener("on_message")
    async def greet(self, message):
        if message.author.id == self.user.id:
            return
#         async with checkSentenceMatch("Hello bot", message.content) as match_percent:
        async with model.predict([f"stsb sentence1: Hello bot sentence2: {message.content}"])[0] as match_rate:
            match_percent = await ((float(match_rate) * 100) / 5)
            if match_percent > 20:
                await message.channel.send(f"I'm like... {int(round(match_percent,0))}% confident that you said 'Hello' to me. If I'm correct, then I just want to make sure you know that I appreciate it.")
#                 await self.process_commands(message)
        
def setup(bot):
    bot.add_cog(images(bot))

    