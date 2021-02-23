import sys
sys.path.append('codeinterview-sandbox')

import asyncio
import discord

import config
import pastebin
from collections import deque
from sandbox import Sandbox, MemoryLimitExceeded, TimeoutError 

TIME_LIMIT = 60
MEM_LIMIT = '1024m'

client = discord.Client()
queue = deque(maxlen=100)

def override_language(language):
        if 'python' in language: return 'python3.6'
        if language == 'c++': return 'cpp'
        return language

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


def is_code_message(message):
    return message.content.startswith('```') and message.content.endswith('```')

def should_ignore_message(message):
    channel = message.channel

    return any([message.author == client.user,
                channel.id not in config.get('allowed_channels')])

async def send_message(channel, msg):
    # TODO: chunk the message into 2000 characters each
    return await channel.send(msg[:2000])

async def send_code_output(channel, language, code):
    output = exec_code(language, code)
    await send_message(channel, 'Output:\n{0}'.format(output))

@client.event
async def on_message(message):
    if should_ignore_message(message):
        return

    channel = message.channel
    
    if is_code_message(message):
        language, code = parse_code_message(message)
        await send_code_output(channel, language, code)
    elif message.content == '!random':
        # THIS IS REALLY, REALLY DUMB :)
        paste = pastebin.random_archive(lambda a: a.syntax in {'c++', 'java', 'python', 'swift', 'scala'})
        code = pastebin.download_paste(paste)
        language = override_language(paste.syntax)

        await send_message(channel, f'```{language}\n{code[:1950]}```')
        await send_message(channel, f'Paste: {paste.url}')
        confirmation_message = await send_message(channel, 'React with 👍 if we should run this code')
        queue.append({
            'channel': channel,
            'confirmation_message_id': confirmation_message.id,
            'random_code': code,
            'language': language
        })

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == '👍':
        for random_code_details in queue:
            if reaction.message.id == random_code_details['confirmation_message_id']:
                await send_message(random_code_details['channel'], 'Executing random code...')
                await send_code_output(random_code_details['channel'],
                                    random_code_details['language'],
                                    random_code_details['random_code'])
    

if __name__ == '__main__':
    print(discord.__version__)
    client.run(config.get('bot_token'))
