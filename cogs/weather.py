from discord.ext import commands
import requests


class Weather(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='weather', aliases=['w', 'wthr', 'temp'])
    async def get_weather(self, message_or_context):
        """Provides the current weather for a given city."""
        if isinstance(message_or_context, commands.context.Context):
            message = message_or_context.message
        else:
            message = message_or_context
        search_term = message.content
        search_term = search_term.replace(search_term.split(' ', 1)[0], '')
        search_term = search_term.strip()
        # URL encode the search_term
        search_term_encoded = search_term.replace(' ', '%20')
        if search_term == '':
            search_term = 'Dallas'
        url = f'https://wttr.in/{search_term_encoded}?format=3'
        response = requests.get(url)
        if response.status_code == 200 and hasattr(response, 'text'):
            weather = response.text.split(":")[1].strip()
            await message.channel.send(weather)
        else:
            await message.channel.send(f"Something went wrong with your search for '{search_term}'. Either the city is not found, or the weather service is down.")


def setup(bot):
    bot.add_cog(Weather(bot))
