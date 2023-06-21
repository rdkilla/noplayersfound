import os
import time
import json
import discord
import openai
from gtts import gTTS
from discord import Intents, File
from dotenv import load_dotenv
import sys
import aiohttp
import asyncio
import base64
from io import BytesIO
from PIL import Image


# Replace with your OBS WebSocket host, port, and password
host = "localhost"
port = 4455
password = "iFocgin19N6XzK9N"

load_dotenv()

#API_URL = 'http://127.0.0.1:7861/sdapi/v1/txt2img'  # replace with your actual API URL
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
        return self.history[-2:]  # get the last 2 messages
    def get_last_player(self):
        return self.history[-1:][0]['content']  # get last player message content
    def get_next_last_player(self):
        return self.history[-2:][0]['content']  # get last player message content
   
conversation = Conversation("history.json")

BOT_ROLE = """
# respond as an advanced AI playing the character of a dungeon master in a perpetual game of dungeons and dragons. describe events, people, places in great detail to create a vivid detailed world for the player to exist in. you give details descriptions of outcomes, movements, attacks, acts of god. You always try to end your response with a question about what the player wants to do next.
"""

PLAYER_ROLE = """
# You are an advanced AI model simulating a player character in a game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DM), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the game world.
"""
async def send_large_message(channel, message_text):
    if len(message_text) <= 2000:
        await channel.send(message_text)
    else:
        parts = [message_text[i:i+2000] for i in range(0, len(message_text), 2000)]
        for part in parts:
            await channel.send(part)
            
def save_base64_image(image_data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.b64decode(image_data))

 
def start_bot(discord_api_key, openai_api_key, bot_role, bot_model, openai_server, api_url):
    openai.api_key = openai_api_key
    openai.api_base = openai_server  # replace hardcoded URL with dynamic server
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        response_text=''
        start_time = time.time() 
        if message.author == client.user:
            return
        
        message_content = message.content[len('!chat '):]
        if message.content.startswith('!chat'):
            loop = asyncio.get_event_loop()
            last_player_message = conversation.get_last_player()
            next_last_player_message = conversation.get_next_last_player()
            response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
                    model=bot_model,
                    max_tokens=440,
                    chat_prompt_size=2000,
                    messages=[
                        {"role": "system", "content" : bot_role},
                        {"role": "assistant", "content" : next_last_player_message},
                        {"role": "assistant", "content" : last_player_message},
                        {"role": "user", "content":  message_content + "describe all the events that need to take place to advance the story, and set up the events for the next step in the story.be inspired by what you know about OSE but don't tell me about OSE"}
                    ]
                    
                    )   
                )
            response_text = response['choices'][0]['message']['content'].replace('</s>', '')
            # write user message to player.txt
            with open('player.txt', 'w') as file:
                file.write(message_content)

            # write bot response to dmaster.txt
            with open('dmaster.txt', 'w') as file:
                file.write(response_text)

            # Add assistant's response to conversation history
            conversation.add_message("assistant", response_text)
            # Generate audio from response text
            tts = gTTS(text=response_text, lang='en',tld='co.uk')
            tts.save("response.mp3")  # save audio file
            # Send response
            await send_large_message(message.channel, response_text)
            
            data = {
                'prompt': 'fantasy role play theme 1980s low budget ' + response_text,
                'steps': 50,  # modify as needed
            }

            session = aiohttp.ClientSession()
                # Send the POST request
            async with session.post(API_URL, json=data) as resp:  # replace hardcoded API_URL with dynamic api_url
                    image_response = await resp.json()
                    image_data = image_response['images'][0]
                    filename = 'generated_image.png'
                    save_base64_image(image_data, filename)
                    await message.channel.send(file=discord.File(filename))
            
            await session.close()
            end_time = time.time()  # time when request completed
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")
    client.run(discord_api_key)
if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1, press Enter for DM): ")
    
    default_openai_server = 'http://127.0.0.1:5002/v1'
    openai_server = input(f"Enter OpenAI server (press Enter for default {default_openai_server}): ")
    if openai_server == "":
        openai_server = default_openai_server 

    default_api_url = 'http://127.0.0.1:7861/sdapi/v1/txt2img'
    API_URL = input(f"Enter Image Generator API URL (press Enter for default {default_api_url}): ")
    if API_URL == "":
        API_URL = default_api_url 

    if bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, PLAYER_ROLE, "TheBloke_Wizard-Vicuna-13B-Uncensored-HF", openai_server, API_URL)
    else:  # default to DM
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "TheBloke_Wizard-Vicuna-13B-Uncensored-HF", openai_server, API_URL)