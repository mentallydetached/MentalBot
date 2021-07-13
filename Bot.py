
# Import Stack
import discord
import requests
import json
from discord.ext import commands
from pathlib import Path
import os
import discord.abc
from simpletransformers.t5 import T5Model
from matplotlib import pyplot
import matplotlib.ticker as ticker
import matplotlib.patheffects as PathEffects
import pandas as pd
from datetime import date


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

sentiment_file = 'stock_sentiment.json'
latest_news_file = 'stock_news.json'


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
        res = requests.get("https://wttr.in/Dallas?format=3")
        await message.channel.send(res.text.split(":")[1].strip())

    ################
    # Stock prices #
    ################
    chrt_bg_color = '#E7E9ED'
    match_percent = await bot.loop.run_in_executor(None, checkSentenceMatch, "How are gamestop stocks looking or GME stocks doing?", message.content)
    if match_percent > 70:
        if os.path.isfile(f'{message.channel.id}rt.png'):
            os.remove(f'{message.channel.id}rt.png')
        if os.path.isfile(f'{message.channel.id}chrt.png'):
            os.remove(f'{message.channel.id}chrt.png')
        res = None
        res = requests.get(
            f"https://api.twelvedata.com/time_series?symbol=GME&interval=5min&apikey={twelveKey}").json()
        if len(res) > 0:
            data = pd.DataFrame(res['values'])
            data["datetime"] = pd.to_datetime(data["datetime"])
            data["close"] = pd.to_numeric(data["close"])
            data["volume"] = pd.to_numeric(data["volume"])
            data = data[data['datetime'] > pd.Timestamp(
                date.today().year, date.today().month, date.today().day)]
            if len(data) > 0:
                _, ax = pyplot.subplots(facecolor=chrt_bg_color)
                ay = data.plot(
                    x='datetime',
                    y='close',
                    kind='line',
                    legend=False,
                    title=f"Realtime Stock for {res['meta']['symbol']}",
                    ax=ax
                )
                old_val = old_direction = direction = None
                i = 0
                for idx, val in data.iterrows():
                    if not old_val and not direction:
                        text = pyplot.text(
                            val['datetime'], val['close'], "$" + str(round(val['close'], 1)), ha='center', size=8)
                        text.set_path_effects(
                            [PathEffects.withStroke(linewidth=3, foreground='w')])
                    i += 1
                    if old_val:
                        direction = "up" if val['close'] - \
                            old_val > 0 else "down"
                    if direction:
                        if i > 3:
                            if old_direction != direction:
                                text = pyplot.text(
                                    val['datetime'], val['close'], "$" + str(round(val['close'], 1)), ha='center', size=8)
                                text.set_path_effects(
                                    [PathEffects.withStroke(linewidth=3, foreground='w')])
                                i = 0
                        old_direction = direction
                    old_val = val['close']
                az = data.plot(
                    x='datetime',
                    y='volume',
                    secondary_y=True,
                    legend=False,
                    ax=ax,
                    color=(1, 1, 1),
                    linewidth=5
                )
                ax.axes.set_facecolor((0, 0, 0, 0.03))
                ax.right_ax.yaxis.set_major_formatter(
                    ticker.FormatStrFormatter("%d"))
                ax.yaxis.set_major_formatter(
                    ticker.FormatStrFormatter("$%.1f"))
                ax.xaxis.get_label().set_visible(False)
                az.zorder = 2
                ay.zorder = 3
                pyplot.savefig(f'{message.channel.id}rt.png')
                vol = requests.get(
                    f"https://api.twelvedata.com/time_series?symbol=GME&interval=1day&apikey={twelveKey}").json()
                await message.channel.send(f"Current Price: ${round(float(res['values'][0]['close']),2)}  |  Volume: {int(vol['values'][0]['volume']):,}", file=discord.File(f'{message.channel.id}rt.png'))

        res = None
        res = requests.get("https://www.styvio.com/api/gme").json()
        if len(res) > 0:
            if Path(f'{message.channel.id}{latest_news_file}').is_file():
                with open(f'{message.channel.id}{latest_news_file}') as json_file:
                    old_res = json.load(json_file)
            else:
                old_res = None
            with open(f'{message.channel.id}{latest_news_file}', 'w') as outfile:
                json.dump(res, outfile)
            for i in range(1, 6):
                if not old_res or res['newsArticle' + str(i)].strip() != old_res['newsArticle' + str(i)].strip():
                    await message.channel.send(f"({res['newsDate' + str(i)].strip()}) {res['newsSource' + str(i)].strip()} said \"{res['newsArticle' + str(i)]}\".")

        res = None
        res = requests.get("https://www.styvio.com/api/sentiment/gme").json()
        if len(res) > 0:
            if Path(f'{message.channel.id}{sentiment_file}').is_file():
                with open(f'{message.channel.id}{sentiment_file}') as json_file:
                    old_res = json.load(json_file)
            else:
                old_res = None
            with open(f'{message.channel.id}{sentiment_file}', 'w') as outfile:
                json.dump(res, outfile)
            if res != old_res:
                df = pd.DataFrame([[res['stockTwitsPercentBullish'], res['stockTwitsPercentNeutral'], res['stockTwitsPercentBearish'],
                                    res['totalSentiment']]], columns=['Bullish', 'Neutral', 'Bearish', 'Sentiment'])
                _, ax = pyplot.subplots(facecolor=chrt_bg_color)
                ax = df.plot(
                    kind='bar',
                    stacked=True,
                    title=f"GME Sentiment: {df['Sentiment'].item()}",
                    color=['#59a96a', (0, 0, 0, 0.5), '#f71735'],
                    ax=ax
                )
                df['Neutral'].plot.bar(0, 0, bottom=df['Bullish'], color=(
                    0, 0, 0, 0), hatch='//', edgecolor=(0, 0, 0, 0.1), lw=0, ax=ax)
                ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d%%"))
                for rect in ax.patches:
                    height = rect.get_height()
                    width = rect.get_width()
                    x = rect.get_x()
                    y = rect.get_y()
                    label_text = f'{height:.2f}%'
                    label_x = x + width / 2
                    label_y = y + height / 2
                    if height > 0:
                        text = ax.text(label_x, label_y, label_text,
                                       ha='center', va='center', fontsize=8)
                        text.set_path_effects(
                            [PathEffects.withStroke(linewidth=3, foreground='w')])
                ax.xaxis.set_visible(False)
                ax.axes.set_facecolor((0, 0, 0, 0.03))
                pyplot.savefig(f'{message.channel.id}chrt.png')
                await message.channel.send(file=discord.File(f'{message.channel.id}chrt.png'))

automatic_cog_load()

bot.run(token)
