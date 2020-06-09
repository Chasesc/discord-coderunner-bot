import asyncio
import discord

import config

client = discord.Client()

def should_ignore_message(message):
    return any([message.author == client.user,
                message.channel.id not in config.get('allowed_channels')])

@client.event
async def on_message(message):
    if should_ignore_message(message):
        return

    print(message.content, 'in', message.channel)

if __name__ == '__main__':
    print(discord.__version__)
    client.run(config.get('bot_token'))
