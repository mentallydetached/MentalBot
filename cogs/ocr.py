import pytesseract
from discord.ext import commands
import os
import discord
from pathlib import Path
import random
from PIL import Image

tmp_dir = 'cogs/tmp/'

# If the folder doesn't exist, create it
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)

def OCRToString(image_filepath):
    """
    Extract text data into a string
    :param image_filepath:
    :return:
    """
    # Read image with Pillow
    image = Image.open(image_filepath)
    
    # Extract text from image
    ocr_data = pytesseract.image_to_string(image, lang='eng')
    return ocr_data

class OCR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ##########################################################
    # Pull last image posted in channel and OCR text from it #
    ##########################################################

    @commands.command(name='ocr', aliases=['read'])
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def get_text(self, message_or_context):
        """Pulls last image posted in channel and extracts text from it using OCR."""

        # If passed a discord.Context object, get the message from that object.
        if isinstance(message_or_context, commands.context.Context):
            message = message_or_context.message
        else:
            message = message_or_context
        
        # Get the channel ID from the message
        channel = message.channel

        # Get image filepath
        image_name = f'{tmp_dir}{channel.id}'
        image_filepath = None

        # Grab last image posted in channel
        await message.channel.trigger_typing()
        
        # Read channel messages for presence of image
        async for message in channel.history(limit=15):
            if message.attachments:
                # Get attachment file extension
                attachment_extension = message.attachments[0].filename.split('.')[-1]
                # If attachment is an image, save it to disk
                if attachment_extension.lower() in ['jpg', 'png', 'jpeg']:
                    # Download image
                    image_filepath = Path(f'{image_name}.{attachment_extension}')
                    await message.attachments[0].save(image_filepath)
                    break
        if image_filepath is None:
            await message.channel.send('No image found in channel.')
            return

        # Extract text from image
        ocr_data = OCRToString(image_filepath)

        # Send extracted text
        await message.channel.send(f'```{os.linesep.join([s for s in ocr_data.splitlines() if s]).replace("  "," ")[:1990]}```')



    @commands.command(hidden=True)
    @commands.cooldown(1, 5, commands.BucketType.guild)
    async def look_in_image_for_specific_content(self, message_or_context):
        """Pulls last image posted in channel and extracts text from it using OCR."""

        # If passed a discord.Context object, get the message from that object.
        if isinstance(message_or_context, commands.context.Context):
            message = message_or_context.message
        else:
            message = message_or_context
        
        # Get the channel ID from the message
        channel = message.channel

        # Get image filepath
        image_name = f'{tmp_dir}{channel.id}'
        image_filepath = None
        
        # Read channel messages for presence of image
        async for message in channel.history(limit=15):
            if message.attachments:
                # Get attachment file extension
                attachment_extension = message.attachments[0].filename.split('.')[-1]
                # If attachment is an image, save it to disk
                if attachment_extension.lower() in ['jpg', 'png', 'jpeg']:
                    # Download image
                    image_filepath = Path(f'{image_name}.{attachment_extension}')
                    await message.attachments[0].save(image_filepath)
                    break
        if image_filepath is None:
            return

        # Extract text from image
        ocr_data = OCRToString(image_filepath).lower()

        print(ocr_data)

        # Check if specific words are in the image that warrant a response:

        # Covid-19 related words and phrases
        if any(word in ocr_data for word in ['covid-19','coronavirus','vaccine','vaccinate','vax','delta variant','covid','covid variant']):
            await message.channel.send('Man... f*ck covid.')
            return
        
        # Fast and the furious related words and phrases
        if any(word in ocr_data for word in ['family','fast and the furious','dominic toretto','mia toretto','fast and furious','too fast too furious','flying car']):
            await message.channel.send(random.choice(['If I win, I take the cash, and I take the respect.','Now you owe me a ten second car.','Nothing really maters unless you have a code.','Nobody else. Just you and me, once and for all.','We do what we do best. We improvise.', 'The world has a way of changing, but there\'s some thing that always stay the same.', 'The most important thing in life will always be the people in this room. Right here, right now.','You\'ve got the best crew in the world standing right in front of you, give them a reason to stay.', 'I live my life a quarter mile at a time.']))
            return
        
        # GME related words and phrases
        if any(word in ocr_data for word in ['gme','moass','diamond hands','hodl','hodlin','gamestop','hodling','short hedge funds','short hedge fund','stonk']):
            await message.channel.send('💎👐')
            return

        # Spongebob related words and phrases
        if any(word in ocr_data for word in ['spongebob','squarepants','patrick star','plankton','squidward','sandy']):
            await message.channel.send(random.choice(['I\'m ready, I\'m ready.', 'If you believe in yourself, with a tiny pinch of magic all your dreams can come true!','F is for friends who do stuff together!','It\'s not just a boulder, it\'s a rock. 🪨']))
            return

        # Dragon Ball Z related words and phrases
        if any(word in ocr_data for word in ['kakarot','goku','vegeta','krillin','trunks','bulma','gohan','frieza','piccolo','dragon ball','yamcha','dbz','mr satan']):
            await message.channel.send('IT\'S OVER 9,000!!!!!!')
            return


def setup(bot):
    bot.add_cog(OCR(bot))
