import os
import discord
import openai
from discord import Intents
from dotenv import load_dotenv
import sys
import argparse

load_dotenv()

dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')
def start_bot(discord_api_key, openai_api_key, bot_role, bot_model):
    # set the OpenAI's API key and base URL
    openai.api_key = openai_api_key
    openai.api_base = 'http://127.0.0.1:5002/v1'

    # initialize discord client
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        if message.content.startswith('!chat'):
            message_content = message.content[len('!chat '):]
            response = openai.ChatCompletion.create(
                model=bot_model, 
                messages=[
                    {"role": "system", "content": bot_role},
                    {"role": "user", "content": message_content}
                ]
            )
            
            response_text = "!chat " + response['choices'][0]['message']['content'].replace('</s>', '')
            await message.channel.send(response_text)
            return

    client.run(discord_api_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose which bot to start.")
    parser.add_argument("bot_type", type=str, choices=["DM", "P1"],
                        help="The type of bot to start (DM or P1).")

    args = parser.parse_args()

    if args.bot_type == "DM":
        start_bot(dm_discord_api_key, dm_openai_api_key, "You are the supreme Dungeon Master...", "ehartford_WizardLM-13B-Uncensored")
    elif args.bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, "You are a helpful assistant.", "ehartford_WizardLM-13B-Uncensored")
        

