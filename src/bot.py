import sys
sys.path.append('codeinterview-sandbox')

import asyncio
import discord

import config
from sandbox import Sandbox, MemoryLimitExceeded, TimeoutError 

TIME_LIMIT = 60
MEM_LIMIT = '1024m'

client = discord.Client()

def parse_code_message(message):
    '''
    extracts the language & code from a message.

    example:
    ```python
    print("Hello, world")
    ```
    '''
    def override_language(language):
        if 'python' in language: return 'python3.6'
        return language
    
    split_message = message.content.split('\n')

    language = split_message[0][3:].strip()
    code = '\n'.join(split_message[1:-1])

    return override_language(language), code

def exec_code(language, code):
    try:
        return Sandbox(time_limit=TIME_LIMIT, memory_limit=MEM_LIMIT).run(language, code)
    except MemoryLimitExceeded:
        return "We ran out of memory. The limit is {0}".format(MEM_LIMIT)
    except TimeoutError:
        return "Timeout: code took too long to run. The time limit is {0} seconds".format(TIME_LIMIT)
    except AssertionError:
        return "Unsupported language..."

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
    
    language, code = parse_code_message(message)
    
    output = exec_code(language, code)
    await send_message(channel, 'Output:\n{0}'.format(output))

if __name__ == '__main__':
    print(discord.__version__)
    client.run(config.get('bot_token'))
