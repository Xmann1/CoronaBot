import discord

with open("token.txt") as fr:
    token = fr.read()


class CoronaBot(discord.Client):
    def __init__(self):
        super().__init__()


client = CoronaBot()
client.run(token)
