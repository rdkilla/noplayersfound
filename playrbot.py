import os
import time
import json
import discord
import openai
import sys
import aiohttp
import asyncio
import base64
from io import BytesIO
from PIL import Image
from gtts import gTTS
from discord import Intents, File
from dotenv import load_dotenv

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
        self.last_dmaster_message = None  # add this line

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
    def get_last_dmaster(self):
        return self.history[-1:][0]['content']  # get last player message content
    def get_next_last_dmaster(self):
        return self.history[-2:][0]['content']  # get last player message content
   
conversation = Conversation("history.json")

BOT_ROLE = """
# respond as an advanced AI playing the character of a dungeon master in a perpetual game of dungeons and dragons. describe events, people, places in great detail to create a vivid detailed world for the player to exist in. you give details descriptions of outcomes, movements, attacks, acts of god. You always try to end your response with a question about what the player wants to do next.
"""

PLAYER_ROLE = """
# You are an advanced AI model simulating a player character in a perpetual game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DMaster), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the game world.
"""
async def send_large_message(channel, message_text):
    if len(message_text) <= 2000:
        await channel.send(message_text)
    else:
        parts = [message_text[i:i+2000] for i in range(0, len(message_text), 2000)]
        for part in parts:
            await channel.send(part)


def create_gif(image_files, output_file, duration):
    images = [Image.open(image_file) for image_file in image_files]
    images[0].save(output_file, save_all=True, append_images=images[1:], optimize=False, duration=duration, loop=0)
            
def save_base64_image(image_data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.b64decode(image_data))

def split_text_into_thirds(text):
    third_length = len(text) // 3
    return text[:third_length], text[third_length:2*third_length], text[2*third_length:]
 
def start_bot(discord_api_key, openai_api_key, bot_role, bot_model, openai_server, api_url):
    openai.api_key = openai_api_key
    openai.api_base = openai_server  # replace hardcoded URL with dynamic server
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        start_time = time.time() 
        DM_BOT_ID = 1114652736068276314  # replace with actual DM bot's ID

        if message.author == client.user:
            return
                
        # If the message is from the DM and does not have attachments, store it
        if message.author.id == DM_BOT_ID and not message.attachments:
            conversation.last_dmaster_message = message.content  # store this message
    
        # If the message is from the DM and it has attachments, respond to the last stored message
        elif message.author.id == DM_BOT_ID and message.attachments and conversation.last_dmaster_message is not None:
            print(f"received player chat request")

            loop = asyncio.get_event_loop()

            # Use the last stored message
            message_content = conversation.last_dmaster_message
            conversation.last_dmaster_message = None  # clear the stored message

            with open('player.txt', 'r') as file:
                last_player_text = file.read()

                response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
                    model=bot_model,
                    max_tokens=600,
                    chat_prompt_size=3000,
                    messages=[
                        {"role": "system", "content" : bot_role},
                        {"role": "user", "content":  message_content + "be concise in your response"}
                    ]
                    )   
                )
                response_text = response['choices'][0]['message']['content'].replace('</s>', '')
                await send_large_message(message.channel, "!chat " + response_text)
     
        
    client.run(discord_api_key)
if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1, press Enter for DM): ")
    
    default_openai_server = 'http://127.0.0.1:5001/v1'
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