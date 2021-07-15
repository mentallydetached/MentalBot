import discord
import json
from discord.ext import commands
import os
import discord.abc
from simpletransformers.t5 import T5Model

model_args = {
    "use_cuda": False,
    "silent": True,
    "verbose": False,
    "use_multiprocessed_decoding": False,
}

model = T5Model(
    "t5",
    "t5-small",
    use_cuda=False,
    args=model_args
)


class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=discord.Color(0x57F287), description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)


#################
# Variable Defs #
#################

help_command = commands.DefaultHelpCommand(no_category='Other Commands')
with open('config.json') as json_file:
    config = json.load(json_file)
# pulls the bot tokens from the hidden config file
token = str(config.get("token"))
twelveKey = str(config.get("twelveKey"))
newsKey = str(config.get("newsKey"))

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description="A simple bot designed to annoy people.",
    help_command=None
)

bot.help_command = MyHelpCommand()


#################
# Function Defs #
#################

def automatic_cog_load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')


##############
# Bot Events #
##############

@bot.event
async def on_ready():
    print("Bot is operational!")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


################
# Bot Commands #
################

@commands.is_owner()
@bot.command()
async def shutdown(ctx):
    """Allows the owner of the bot to shut down the bot from within Discord."""
    e = discord.Embed(colour=discord.Colour(0x57F287),
                      description="Command Received, Shutting down Bot!")
    await ctx.send(embed=e)
    exit()


def checkSentenceMatch(sentence1, sentence2):
    match_rate = model.predict(
        [f"stsb sentence1: {sentence1} sentence2: {sentence2}"])[0]
    match_percent = ((float(match_rate) * 100) / 5)
    return match_percent


################
# Bot Listener #
################

@bot.listen()
async def on_message(message):

    ###########
    # Weather #
    ###########
    match_percent = await bot.loop.run_in_executor(None, checkSentenceMatch, "What's the weather", message.content)
    if match_percent > 80:
        context = await bot.get_context(message)
        await bot.get_command('weather').callback(context, message)

    ################
    # Stock prices #
    ################
    match_percent = await bot.loop.run_in_executor(None, checkSentenceMatch, "How are gamestop stocks looking or GME stocks doing or gamestops stonks?", message.content)
    if match_percent > 75:
        context = await bot.get_context(message)
        await bot.get_command('stock').callback(context, message)

automatic_cog_load()

bot.run(token)
