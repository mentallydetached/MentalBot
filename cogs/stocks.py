from discord.ext import commands
import requests
import json
from matplotlib import pyplot
import matplotlib.ticker as ticker
import matplotlib.patheffects as PathEffects
import matplotlib.dates as mdates
import pandas as pd
from datetime import date
import os
import discord
from pathlib import Path
from PIL import Image
import yfinance
from alpha_vantage.timeseries import TimeSeries

with open('config.json') as json_file:
    config = json.load(json_file)
# pulls the bot tokens from the hidden config file
alphaKey = str(config.get("alphaKey"))

tmp_dir = 'cogs/tmp/'
sentiment_file = 'stock_sentiment.json'
latest_news_file = 'stock_news.json'
realtime_chart_image = 'rt.png'
sentiment_chart_image = 'chrt.png'

# If the folder doesn't exist, create it
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)


class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ############################################################################
    # Send a request to the yahoo stock API and returns the latest stock data  #
    ############################################################################

    @commands.command(name='stock', aliases=['s', 'stocks', 'get_stock', 'get_stocks'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def get_stock(self, message_or_context):
        """Performs a search and creates charts for the latest stock data, news, and sentiment for a given stock."""

        # If passed a discord.Context object, get the message from that object.
        if isinstance(message_or_context, commands.context.Context):
            message = message_or_context.message
        else:
            message = message_or_context

        # Grab last image posted in channel
        await message.channel.trigger_typing()

        # Get search term from message content (if present)
        search_term = message.content

        # If the message does not start with the ! prefix or contains more than 1 space, set search_term to blank value
        if len(search_term.split(' ')) > 2 or not search_term.startswith('!'):
            search_term = ''
        else:
            search_term = search_term.replace(search_term.split(' ', 1)[0], '')
        search_term = search_term.strip()
        search_term = search_term.upper()

        # Set a default search_term if one was not provided
        if search_term == '':
            search_term = 'GME'

        # Get channel id from the message context
        channelID = message.channel.id

        # Set the background color for the charts
        chrt_bg_color = '#E7E9ED'

        # Set varaibles for chart images and data
        chrt_rt = f'{tmp_dir}{channelID}{search_term}{realtime_chart_image}'
        chrt_sentiment = f'{tmp_dir}{channelID}{search_term}{sentiment_chart_image}'
        json_news = f'{tmp_dir}{channelID}{search_term}{latest_news_file}'
        json_sentiment = f'{tmp_dir}{channelID}{search_term}{sentiment_file}'

        # If the file exists, delete it
        if os.path.isfile(chrt_rt):
            os.remove(chrt_rt)
        if os.path.isfile(chrt_sentiment):
            os.remove(chrt_sentiment)

        logo = None
        res = None

        # Pull stocks from Yahoo Stocks API
        res = yfinance.Ticker(search_term)

        # If the stock data is not found, return an error message
        if res is None:
            await message.channel.send(f'An error occurred: Could not find stock data for {search_term}.')
            return
        # If the stock data is found, create charts
        else:
            # Create a list of the stock data
            stock_data = res.info
            current_price = stock_data['currentPrice']
            short_ratio = stock_data['shortRatio']
            current_high = stock_data['dayHigh']
            current_low = stock_data['dayLow']
            total_volume = stock_data['volume']

            # Get logo
            logo = stock_data['logo_url']
            if not logo:
                logo = "https://cdn.discordapp.com/avatars/681652927370362920/ce20405193570c8bfdc6c4a1245d970a.webp?size=128"

            # Convert the logo URL to a PIL image and resize
            logo_img = Image.open(requests.get(logo, stream=True).raw)
            logo_img.thumbnail((65, 65))
            plt, ax = pyplot.subplots(facecolor=chrt_bg_color)

            # Add stock logo to the bottom left of the figure with a fixed width and height
            pyplot.figimage(logo_img, xo=0, yo=0, alpha=0.6)

            # Add the short_ratio to the bottom right of the figure
            plt.text(0.99, 0.01, f'Short Ratio: {short_ratio}', color='black', fontsize=12, verticalalignment='bottom', horizontalalignment='right')

            # Add a ticker with the rest of the stock data to the top of the figure
            plt.text(0.01, 0.99, f'Curr Price {current_price}   Day Low {current_low}   Day High {current_high}   Total Vol {total_volume}', color='black', fontsize=9, verticalalignment='top', horizontalalignment='left')

            # Get the intraday stock data from the Alpha Vantage API
            ts = TimeSeries(key=alphaKey, output_format='pandas')
            df, meta_data = ts.get_intraday(symbol=search_term,interval='1min', outputsize='compact')
            df.reset_index(inplace=True) 
            df['date'] = pd.to_datetime(df['date'])
            df["4. close"] = pd.to_numeric(df["4. close"])
            df["5. volume"] = pd.to_numeric(df["5. volume"])
            df = df[df['date'] > pd.Timestamp(date.today().year, date.today().month, date.today().day)]

            # Grab only the latest 50 records
            df = df.head(50)

            if len(df) > 0:
                ay = df.plot(
                    x='date',
                    y='4. close',
                    kind='line',
                    legend=False,
                    title=f"{search_term.upper()} Stock as of {df['date'].head(1).item().strftime('%I:%M %p')}",
                    ax=ax
                )
                old_val = old_direction = direction = None
                i = 0
                for _, val in df.iterrows():
                    if not old_val and not direction:
                        text = pyplot.text(
                            val['date'], val['4. close'], "$" + str(round(val['4. close'], 1)), ha='center', size=8)
                        text.set_path_effects(
                            [PathEffects.withStroke(linewidth=3, foreground='w')])
                    i += 1
                    if old_val:
                        direction = "up" if val['4. close'] - \
                            old_val > 0 else "down"
                    if direction:
                        if i > 3:
                            if old_direction != direction:
                                text = pyplot.text(
                                    val['date'], val['4. close'], "$" + str(round(val['4. close'], 1)), ha='center', size=8)
                                text.set_path_effects(
                                    [PathEffects.withStroke(linewidth=3, foreground='w')])
                                i = 0
                        old_direction = direction
                    old_val = val['4. close']
                az = df.plot(
                    x='date',
                    y='5. volume',
                    secondary_y=True,
                    legend=False,
                    ax=ax,
                    color=(1, 1, 1),
                    linewidth=5
                )
                ax.axes.set_facecolor((0, 0, 0, 0.03))
                # Format the datetime in the x-axis to only show timestamp as 12 hour time
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))
                ax.yaxis.set_major_formatter(
                    ticker.FormatStrFormatter("$%.1f"))
                ax.xaxis.get_label().set_visible(False)
                az.zorder = 2
                ay.zorder = 3
                pyplot.savefig(chrt_rt)
                pyplot.close()
            else:
                await message.channel.send(f'An error occurred: No data found for {search_term}.')
                return


            await message.channel.send(f"Current Price: ${round(float(current_price),2)}  |  Volume: {int(total_volume):,}", file=discord.File(chrt_rt))

        res = None
        res = requests.get(f"https://www.styvio.com/api/{search_term}").json()
        if len(res) > 0:
            if Path(json_news).is_file():
                with open(json_news) as json_file:
                    old_res = json.load(json_file)
            else:
                old_res = None
            with open(json_news, 'w') as outfile:
                json.dump(res, outfile)
            for i in range(1, 6):
                if not old_res or res['newsArticle' + str(i)].strip() != old_res['newsArticle' + str(i)].strip():
                    await message.channel.send(f"({res['newsDate' + str(i)].strip()}) {res['newsSource' + str(i)].strip()} said \"{res['newsArticle' + str(i)]}\".")

        res = None
        res = requests.get(
            f"https://www.styvio.com/api/sentiment/{search_term}").json()
        if len(res) > 0:
            if Path(json_sentiment).is_file():
                with open(json_sentiment) as json_file:
                    old_res = json.load(json_file)
            else:
                old_res = None
            with open(json_sentiment, 'w') as outfile:
                json.dump(res, outfile)
            if res != old_res:

                if not logo:
                    # Perform API call to get stock image URL
                    try:
                        logo = requests.get(
                            f"https://www.styvio.com/api/{search_term}").json()['logoURL']
                    except:
                        pass
                    if not logo:
                        logo = "https://cdn.discordapp.com/avatars/681652927370362920/ce20405193570c8bfdc6c4a1245d970a.webp?size=128"

                # Convert the logo URL to a PIL image and resize
                logo_img = Image.open(requests.get(logo, stream=True).raw)
                logo_img.thumbnail((65, 65))

                df = pd.DataFrame([[res['stockTwitsPercentBullish'], res['stockTwitsPercentNeutral'], res['stockTwitsPercentBearish'],
                                    res['totalSentiment']]], columns=['Bullish', 'Neutral', 'Bearish', 'Sentiment'])
                _, ax = pyplot.subplots(facecolor=chrt_bg_color)

                # Add stock logo to the bottom left of the chart
                pyplot.figimage(logo_img, 0, 0, alpha=.5)

                ax = df.plot(
                    kind='bar',
                    stacked=True,
                    title=f"{search_term} Sentiment: {df['Sentiment'].item()}",
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
                pyplot.savefig(chrt_sentiment)
                await message.channel.send(file=discord.File(chrt_sentiment))


def setup(bot):
    bot.add_cog(Stocks(bot))
