import datetime
import discord
import random
import sys
import os

token = sys.argv[1]


class CoronaBot(discord.Client):
    def __init__(self):
        super().__init__()

        self.permission_denied_warned_servers = []
        self.corona_emoji = "<:corona:684132221077946401>"
        self.protected_message_contents = ["(This message is not infectious)"]
        self.max_infection_time = 600
        self.infectious_message_delay = 3600  # This means by one hour there is a 50/50 chance of an infectious message
        self.log_file = "./log.txt"

        self.bind_events()

    def bind_events(self):
        @self.event
        async def on_ready():
            await self.event_on_ready()

        @self.event
        async def on_message(ctx):
            await self.event_on_message(ctx)

    async def event_on_ready(self):
        self.log(f"Bot started as {self.user.name}")

    async def event_on_message(self, msg):
        self.log_message(msg)

        corona_role = discord.utils.get(msg.guild.roles, name="Corona infected")
        if corona_role is None:
            self.log("No corona role detected in server, attempting to create one")
            try:
                corona_role = await msg.guild.create_role(name="Corona infected", color=discord.Color(0xff0000))
                await msg.guild.get_member(self.user.id).add_roles(corona_role)

            except PermissionError:
                self.log("Permission error, need Manage roles permission")
                if msg.guild.id not in self.permission_denied_warned_servers:
                    self.permission_denied_warned_servers.append(msg.guild.id)
                    await msg.channel.send("I do not have permission to manage roles")
                else:
                    self.log("Suppressing warning since server has already been warned before")

            else:
                await msg.channel.send("Corona has been detected in this server")

        if corona_role is not None:
            latest_messages = []

            async for earlier_message in msg.channel.history(limit=3):
                latest_messages.append(earlier_message)

            preceding_message = latest_messages[1]
            preceding_author = preceding_message.author
            preceding_author_is_me = self.user.id == preceding_author.id

            author_has_corona = msg.author in corona_role.members

            seconds_passed_since_preceding_message = msg.created_at.timestamp() - preceding_message.created_at.timestamp()

            if not author_has_corona:
                self.log("  Earlier messages:")

                for earlier_message in latest_messages:
                    self.log_message(earlier_message, prefix="  > ")

                self.log(f"    Last message:")
                self.log_message(preceding_message, prefix="  > ")

                if preceding_author_is_me and not self.is_infectious(preceding_message.content):
                    self.log("Last message is by me and is not infectious")

                else:
                    preceding_author_has_corona = preceding_author in corona_role.members
                    if preceding_author_has_corona:
                        self.log("Preceding author has corona")

                        self.log(f"{round(seconds_passed_since_preceding_message, 0)} seconds have passed since preceding message")

                        if seconds_passed_since_preceding_message < self.max_infection_time:
                            self.log("USER GOT INFECTED!")

                            await msg.author.add_roles(corona_role)
                            await msg.channel.send(f"{self.corona_emoji * 3} **Uh oh! It looks like you have been infected :flushed:** (This message is not infectious) {self.corona_emoji * 3}")

                        else:
                            self.log("Infection has died in this message")

            if not msg.author.id == self.user.id:
                n = self.infectious_message_delay // seconds_passed_since_preceding_message
                num = random.randint(0, n)

                self.log(f"Chance of random message: 1/{int(n)} number generated: {num}")

                if num == 0:
                    await msg.channel.send(":wave:")

        try:
            if str(self.user.id) in msg.content:
                await msg.channel.send("Bruh")
        except UnicodeDecodeError:
            pass

    def log(self, message, end="\n"):
        start = datetime.datetime.now().strftime("<%d/%m/%Y %H:%M:%S> ")
        print(message)
        if self.log_file:
            with open(self.log_file, "a") as fa:
                for char in start + message + end:
                    try:
                        fa.write(char)
                    except UnicodeDecodeError:
                        pass

    def is_infectious(self, message_content):
        for protected_message_content in self.protected_message_contents:
            if protected_message_content in message_content:
                return False

        return True

    def log_message(self, msg, prefix=""):
        if msg.guild:
            if msg.author.display_name != msg.author.name:
                self.log(f"{prefix}[{msg.guild.name}/{msg.channel.name}] {msg.author.name}#{msg.author.discriminator} ('{msg.author.display_name}'): {msg.content}")
            else:
                self.log(f"{prefix}[{msg.guild.name}/{msg.channel.name}] {msg.author.name}#{msg.author.discriminator}: {msg.content}")
        else:
            self.log(f"{prefix}[DM/{msg.channel.recipient}] {msg.author.name}#{msg.author.discriminator}: {msg.content}")


client = CoronaBot()
client.run(token)