import os
import discord
import openai
from discord import Intents

# set the OpenAI's API key and base URL
openai.api_key = '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'
openai.api_base = 'http://127.0.0.1:5002/v1'

# initialize discord client
intents = Intents.default()
intents.messages = True
intents.message_content = True
client2 = discord.Client(intents=intents)

# define what to do on new message
@client2.event
async def on_message(message):
    # don't respond to ourselves
    print(f"message received from {message.author} in {message.channel}")
    if message.author == client2.user:
        print(f"i see that it was sent by me!")
        return
    if message.content.startswith('!chat1'):
        print(f"message from {message.author} starts with !chat1")
        # get the text after the "!chat" command
        message_content = message.content[len('!chat1 '):]

        # use openai API to get a response
        response = openai.ChatCompletion.create(
            model="ehartford_WizardLM-13B-Uncensored",  # or "text-curie-003"
            messages=[
                {"role": "system", "content": "You are the supreme Dungeon Master, and host games of dungeons and dragons.  you guide the adventure and roll dice often to find out what happens next"},
                {"role": "user", "content": message_content}
            ]
        )
        
        # send the message back
        response_text = "!chat2 " + response['choices'][0]['message']['content'].replace('</s>', '')
        await message.channel.send(response_text)
        return
# login to discord
client2.run('MTExNDY1MjczNjA2ODI3NjMxNA.GOmaNp.K8KatEpoZ0A9Me6vq5wIYp-WM4vuzipluO1FfY')