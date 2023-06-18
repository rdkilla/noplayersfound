import os
import time
import json
import discord
import openai
from discord import Intents, File
from dotenv import load_dotenv
import sys
import aiohttp
import base64
from io import BytesIO
from PIL import Image

load_dotenv()

API_URL = 'http://127.0.0.1:7861/sdapi/v1/txt2img'  # replace with your actual API URL
dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')

class Conversation:
    def __init__(self, history_file):
        self.history_file = history_file
        self.load_history()

    def load_history(self):
        try:
            with open(self.history_file, 'r') as file:
                self.history = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []
            self.save_history()  # create file with empty list if not existent or invalid

    def save_history(self):
        with open(self.history_file, 'w') as file:
            json.dump(self.history, file)

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 50:  # if more than 50 messages, remove the oldest one
            del self.history[0]
        self.save_history()  # save after every addition

    def get_messages(self):
        return self.history[-6:]  # get the last 6 messages
        
conversation = Conversation("history.json")

BOT_ROLE = """
# You s Dungeon Master in a Dungeons & Dragons (D&D) game. Your create the story live during the game, and generate vivid descriptions of scenes. You always try to end your response with a question about what the player wants to do next.
"""

PLAYER_ROLE = """
# You are an advanced AI model simulating a player character in a game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DM), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the game world.
"""

def save_base64_image(image_data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.b64decode(image_data))

def start_bot(discord_api_key, openai_api_key, bot_role, bot_model):
    openai.api_key = openai_api_key
    openai.api_base = 'http://127.0.0.1:5002/v1'
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        response_text=''
        if message.author == client.user:
            return
        start_time = time.time()  # time when request initiated
        message_content = message.content[len('!chat '):]
        if message.content.startswith('!chat'):
            conversation.add_message("user", message_content)
            response = openai.ChatCompletion.create(
                model=bot_model, 
                messages=conversation.get_messages()
            )
            response_text = response['choices'][0]['message']['content'].replace('</s>', '')

            # Add assistant's response to conversation history
            conversation.add_message("assistant", response_text)

            # Send response
            await message.channel.send(response_text)

            data = {
                'prompt': 'fantasy role play theme 1980s low budget' + response_text,
                'steps': 22,  # modify as needed
            }

            session = aiohttp.ClientSession()
                # Send the POST request
            async with session.post(API_URL, json=data) as resp:
                    image_response = await resp.json()
                    image_data = image_response['images'][0]
                    filename = 'generated_image.png'
                    save_base64_image(image_data, filename)
                    await message.channel.send(file=discord.File(filename))
            end_time = time.time()  # time when request completed
            elapsed_time = end_time - start_time
            await session.close()
            print(f"Elapsed time: {elapsed_time} seconds")  # print the elapsed time    

    client.run(discord_api_key)

if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1, press Enter for DM): ")
    if bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, PLAYER_ROLE, "text-davinci-003")
    else:  # default to DM
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "text-davinci-003")