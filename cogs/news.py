from discord.ext import commands
import requests
import json


with open('config.json') as json_file:
    config = json.load(json_file)
# pulls the bot tokens from the hidden config file
newsKey = str(config.get("newsKey"))


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #####################################################################
    # Send a request to the public news API and returns the latest news #
    #####################################################################

    @commands.command(name='news', aliases=['news_api'])
    async def get_latest_news(self, ctx):
        """Performs a search for the current top headlines for a given topic."""
        search_term = ctx.message.content
        search_term = search_term.replace(search_term.split(' ', 1)[0], '')
        if search_term == '':
            search_term = 'Gamestop'
        url = f'https://newsapi.org/v2/top-headlines?q={search_term}&apiKey={newsKey}'
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get('articles'):
            articles = data['articles']
            news_list = []
            for article in articles:
                news_list.append(article['title'])
            news_list = '\n'.join(news_list)
            await ctx.send(news_list)


def setup(bot):
    bot.add_cog(News(bot))
