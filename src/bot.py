import asyncio
import discord

import config

client = discord.Client()

def parse_code_message(message):
    '''
    extracts the language & code from a message.

    example:
    ```python
    print("Hello, world")
    ```
    '''
    split_message = message.content.split('\n')

    language = split_message[0][3:].strip()
    code = '\n'.join(split_message[1:-1])

    return language, code

def should_ignore_message(message):
    channel = message.channel
    content = message.content

    is_code_message = content.startswith('```') and content.endswith('```') 
    return any([message.author == client.user,
                channel.id not in config.get('allowed_channels'),
                not is_code_message])

async def send_message(channel, msg):
    # TODO: chunk the message into 2000 characters each
    return await channel.send(msg[:2000])

@client.event
async def on_message(message):
    if should_ignore_message(message):
        return

    channel = message.channel
    
    print(message.content, 'in', message.channel)
    language, code = parse_code_message(message)

    await send_message(channel, 'language: {0}\ncode: {1}'.format(language, code))

if __name__ == '__main__':
    print(discord.__version__)
    client.run(config.get('bot_token'))
