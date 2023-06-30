import os
import time
import json
import discord
import openai
import sys
import subprocess
import aiohttp
import asyncio
import base64
from aiohttp import ClientSession, ClientTimeout
from subprocess import Popen
from io import BytesIO
from PIL import Image
from gtts import gTTS
from discord import Intents, File
from dotenv import load_dotenv
from base64 import b64decode

timeout = ClientTimeout(total=8000)  # total timeout of 60 seconds

# Replace with your OBS WebSocket host, port, and password
host = "localhost"
port = 4455
password = "iFocgin19N6XzK9N"

load_dotenv()

#txt2img_api_url = 'http://127.0.0.1:7861/sdapi/v1/txt2img'  # replace with your actual API URL
dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')

async def generate_images(txt2img_api_url, response_text):
    third1, third2, third3 = split_text_into_thirds(response_text)
    image_files = []
    for i, third in enumerate([third1, third2, third3]):
        data = {
            'prompt': 'fantasy role play theme 1980s low budget ' + third,
            'steps': 32,  # modify as needed
        }

        timeout = aiohttp.ClientTimeout(total=600)
        session = aiohttp.ClientSession(timeout=timeout)
        # Send the POST request
        async with session.post(txt2img_api_url, json=data) as resp:  # replace hardcoded txt2img_api_url with dynamic txt2img_api_url
            image_response = await resp.json()
            image_data = image_response['images'][0]
            filename = f'generated_image_{i+1}.png'
            save_base64_image(image_data, filename)
            image_files.append(filename)
        await session.close()
    gif_filename = 'animated.gif'
    create_gif(image_files, gif_filename, 1800)  # Duration is in milliseconds
async def generate_image(txt2img_api_url, response_text): 
    data = {
        'prompt': 'fantasy role play theme 1980s low budget ' + response_text,
        'steps': 60,  # modify as needed
        'width': 768,
        'height': 768,
    }

    timeout = aiohttp.ClientTimeout(total=600)
    session = aiohttp.ClientSession(timeout=timeout)
    # Send the POST request
    async with session.post(txt2img_api_url, json=data) as resp:  # replace hardcoded txt2img_api_url with dynamic txt2img_api_url
        image_response = await resp.json()
        image_data = image_response['images'][0]
        filename = f'generated_image.png'
        save_base64_image(image_data, filename)
    await session.close()

async def run_dmaster_facegen():
    process = await asyncio.create_subprocess_exec("dmaster_facegen.bat", cwd=r"D:\ai\discordbot\noplayerfound")

    # This line is non-blocking, allows other tasks to run while waiting
    await process.communicate()

async def run_player_facegen():
    process = await asyncio.create_subprocess_exec("player_facegen.bat", cwd=r"D:\ai\discordbot\noplayerfound")

    # This line is non-blocking, allows other tasks to run while waiting
    await process.communicate()


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
        
    def get_last_dmaster(self):
        if len(self.history) >= 1:  # check if there's at least one entry in history
            return self.history[-1]['content']  # get last dmaster message content
        else:
            return "i don't seem to recall"  # or some default value

    # def get_next_last_dmaster(self):
        # if len(self.history) >= 2:  # check if there's at least two entries in history
            # return self.history[-2]['content']  # get second-to-last dmaster message content
        # else:
            # return None  # or some default value
conversation = Conversation("history.json")

BOT_ROLE = """
respond ONLY as an advanced AI dungeon master in a perpetual game of dungeons and dragons. describe people, places in great detail to create a vivid world for the player to exist in. You describe events to advance and outcomes of player choices to advance the story.  You always try to end your response with a question about what the player wants to do next.
"""

PLAYER_ROLE = """
You are an advanced AI model simulating a player character in a game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DM), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the game world. This message is followed by the last player message, then the last message from you, then the most recent layer message. respond after you analyze the following data:
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
 
def start_bot(discord_api_key, openai_api_key, bot_role, bot_model, openai_server, txt2img_api_url):
    openai.api_key = openai_api_key
    SADTALKER_API_URL = txt2img_api_url.rsplit('/', 1)[0] + '/sadtalker'
    openai.api_base = openai_server  # replace hardcoded URL with dynamic server
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        response_text=''
        message_content = message.content[len('!chat '):]
        start_time = time.time() 
    
        if message.author == client.user:
            return
        if message.content.startswith('!chat'):
            print(f"received chat request")
            loop = asyncio.get_event_loop()
            last_dmaster_message = conversation.get_last_dmaster()
            ttsplayer = gTTS (text=message_content, lang='en',tld='ca')
            ttsplayer.save("playerinput.mp3")
            await run_player_facegen()
            # write user message to player.txt
            with open('player.txt', 'w') as file:
                file.write(message_content)
            #next_last_dmaster_message = conversation.get_next_last_dmaster()
            print("open player.txt")
            with open('player.txt', 'r') as file:
                last_player_text = file.read()
            print("player.txt open, initiate response")
            print(last_player_text)
            print(last_dmaster_message)
            print(message_content)
            response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
                model=bot_model,
                max_tokens=660,
                chat_prompt_size=6000,
                messages=[
                    {"role": "system", "content" : bot_role},
                    {"role": "user", "content" : last_player_text},
                    {"role": "assistant", "content" : last_dmaster_message},
                    {"role": "user", "content":  message_content}
                ]
                )
            )                
                
            print("post chat create")
            response_text = response['choices'][0]['message']['content'].replace('</s>', '')
            
            gif_filename='generated_image.png'           
            # Add assistant's response to conversation history
            conversation.add_message("assistant", response_text)
            
            ttsdmaster = gTTS(text=response_text, lang='en',tld='co.uk')
            ttsdmaster.save("dmasterresponse.mp3")  # save audio file
            
            # Send response
            await send_large_message(message.channel, response_text) 
            
            #generate face animatino and api call for image generation in parallel?
            await asyncio.gather(
                generate_image(txt2img_api_url, response_text),
                run_dmaster_facegen()
            )

            
            # write bot response to dmaster.txt
            with open('dmaster.txt', 'w') as file:
                file.write(response_text)
                
            print("sending picture")
            await message.channel.send(file=discord.File(gif_filename))
            end_time = time.time()  # time when request completed
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")
            
    client.run(discord_api_key)
if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1, press Enter for DM): ")
    
    default_openai_server = 'http://127.0.0.1:5001/v1'
    openai_server = input(f"Enter OpenAI server (press Enter for default {default_openai_server}): ")
    if openai_server == "":
        openai_server = default_openai_server 

    default_txt2img_api_url = 'http://192.168.88.246:7860/sdapi/v1/txt2img'
    txt2img_api_url = input(f"Enter Image Generator API URL (press Enter for default {default_txt2img_api_url}): ")
    if txt2img_api_url == "":
        txt2img_api_url = default_txt2img_api_url 

    if bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, PLAYER_ROLE, "TheBloke_vicuna-33B-preview-GPTQ", openai_server, txt2img_api_url)
    else:  # default to DM
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "TheBloke_vicuna-33B-preview-GPTQ", openai_server, txt2img_api_url)