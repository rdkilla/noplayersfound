import os
import discord
import openai
from discord import Intents

# set the OpenAI's API key and base URL
openai.api_key = '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'
openai.api_base = 'http://127.0.0.1:5001/v1'

# initialize discord client
intents = Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

# define what to do on new message
@client.event
async def on_message(message):
    # don't respond to ourselves
    print(f"message received from {message.author} in {message.channel}")
    if message.author == client.user:
        print(f"i see that it was sent by me!")
        return
    if message.content.startswith('!chat2'):
        print(f"message from {message.author} starts with !chat2")
        # get the text after the "!chat" command
        message_content = message.content[len('!chat2 '):]

        # use openai API to get a response
        response = openai.ChatCompletion.create(
            model="ehartford_WizardLM-13B-Uncensored",  # or "text-curie-003"
            messages=[
                {"role": "system", "content": "You are a player in a game of dungeons and dragons. you will have to constantly make decisions about what to do.  you may ask for d20 dice rolls to help you decide."},
                {"role": "user", "content": message_content}
            ]
        )
        
        # send the message back
        response_text = "!chat1 " + response['choices'][0]['message']['content'].replace('</s>', '')
        await message.channel.send(response_text)
        return
# login to discord
client.run('MTExODY2NDA5ODAwNDA3NDUwNw.GzHXno.G2jxsO1PGZ3MGwjxVou750h6R-H96dOkH7MPrw')