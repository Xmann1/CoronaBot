import discord
import os

token = os.getenv("BOT_TOKEN")


class CoronaBot(discord.Client):
    def __init__(self):
        super().__init__()


client = CoronaBot()
client.run(token)
