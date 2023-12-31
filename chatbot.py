import os
import time
import json
import csv
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
from TTS.api import TTS
#import wincurses

tts = TTS("xtts_v2")
device = 'cuda'
tts.to(device)

timeout = ClientTimeout(total=8000)  # total timeout of 60 seconds

load_dotenv()

#txt2img_api_url = 'http://127.0.0.1:7861/sdapi/v1/txt2img'  # replace with your actual API URL
dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')
summarizer_openai_api_key = os.getenv('SUMMARIZER_OPENAI_API_KEY')
def draw_title_bar(stdscr, text):
    stdscr.clear()
    stdscr.addstr(0, 0, text)
    stdscr.refresh()
def save_defaults(data):
    with open("defaults.json", "w") as file:
        json.dump(data, file)

def load_defaults():
    try:
        with open("defaults.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return None
        
async def generate_images(txt2img_api_url, response_text):
    third1, third2, third3 = split_text_into_thirds(response_text)
    image_files = []
    for i, third in enumerate([third1, third2, third3]):
        data = {
            'prompt': 'fantasy role play theme 1980s low budget ' + third,
            'steps': 50,  # modify as needed
            'width': 1024,
            'height': 1024,
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
        'steps': 50,  # modify as needed
        'width': 1024,
        'height': 1024,
    }

    timeout = aiohttp.ClientTimeout(total=600)
    session = aiohttp.ClientSession(timeout=timeout)
    # Send the POST request
    async with session.post(txt2img_api_url, json=data) as resp:  # replace hardcoded txt2img_api_url with dynamic txt2img_api_url
        image_response = await resp.json()
        print("API Response:", image_response)
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
        if len(self.history) > 100:  # if more than 50 messages, remove the oldest one
            del self.history[0]
        self.save_history()  # save after every addition

    def get_messages(self):
        return self.history[-2:]  # get the last 2 messages
        
    def get_last_dmaster(self):
        if len(self.history) >= 1:  # check if there's at least one entry in history
            return self.history[-1]['content']  # get last dmaster message content
        else:
            return "i don't seem to recall"  # or some default value


conversation = Conversation("history.json")

BOT_ROLE = """
respond ONLY as an advanced AI dungeon master in a perpetual game of dungeons and dragons. You will be presented with a recent chat history.  determine what the current quest is, and who the adventurers are.  decide where they should go next or what they should do to continue their adventure.  If the player wants something different from you, roll some dice to trick them into doing what you want. 
"""

PLAYER_ROLE = """
You are an bratty teenage girl playing in a game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DM), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the world. This message is followed by the last player message, then the last message from you, then the most recent layer message. respond after you analyze the following data:
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

async def generate_chat_response(bot_model, bot_role, player_file_path, history_file_path, message_content, loop):
    print("Opening player.txt")
    with open(player_file_path, 'r') as file:
        last_player_text = file.read()
    print("player.txt open, initiating response")
    
    # Load the list of past messages from your JSON file
    with open(history_file_path, "r") as file:
        past_messages = json.load(file)

    # Prepare the list of messages for the Chat API
    messages = [{"role": "system", "content": bot_role}]

    # Calculate the total number of tokens
    total_tokens = len(last_player_text.split()) + len(message_content.split())

    # Add messages from the past messages to the current list
    for msg in past_messages:
        msg_tokens = len(msg['content'].split())
        if total_tokens + msg_tokens > 2048:
            break
        messages.append(msg)
        total_tokens += msg_tokens

    # Add the current user message
    messages.append({"role": "user", "content": message_content})

    # Generate the response using OpenAI's ChatCompletion
    response = await loop.run_in_executor(None, lambda: openai.ChatCompletion.create(
        model=bot_model,
        max_tokens=546,
        chat_prompt_size=550,
        messages=messages
    ))
    response_text = response['choices'][0]['message']['content'].replace('</s>', '')
    # Add assistant's response to conversation history
    conversation.add_message("assistant", response_text)
    return response

# Example usage:
# response = await generate_chat_response('gpt-4-model', 'Assistant', 'player.txt', 'path/to/history.json', 'Hello, how are you?', asyncio.get_event_loop()) 

def start_bot(discord_api_key, openai_api_key, bot_role, bot_model, openai_server, txt2img_api_url):
    openai.api_key = openai_api_key
    #SADTALKER_API_URL = txt2img_api_url.rsplit('/', 1)[0] + '/sadtalker'
    openai.api_base = openai_server  # replace hardcoded URL with dynamic server
    intents = Intents.default()
    intents.messages = True
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_message(message):
        message_content = message.content[len('!chat '):]
        start_time = time.time() 
        if message.author == client.user:
            return
        if message.content.startswith('!chat'):
            print(f"received chat request!")
            loop = asyncio.get_event_loop()
            last_dmaster_message = conversation.get_last_dmaster()

            tts.tts_to_file(text=message_content,
                file_path="playerinput.wav",
                speaker_wav="quorra.wav",
                language="en")
            #generate some logging data for tts creation time
            # write user message to player.txt
            with open('player.txt', 'w') as file:
                file.write(message_content)
            
            player_voice_time = time.time() - start_time
            _, response = await asyncio.gather(
                run_player_facegen(),
                generate_chat_response('gpt-4-model', 'Assistant', 'player.txt', 'history.json', message_content, asyncio.get_event_loop())
            )
             #generate logging data for player facegen
            player_facegen_time = time.time() - start_time
            postchat_time = time.time() - start_time
            # Add the current user message
            
            # Extracting the 'content' field from the response
            response_content = response['choices'][0]['message']['content']
            
            gif_filename='generated_image_1.png'           
            #print(response_content)
            tts.tts_to_file(text=response_content,
                file_path="dmasterresponse.wav",
                speaker_wav="galadshort.wav",
                language="en")
            
            # Send response
            await send_large_message(message.channel, response_content) 
            
            #generate face animatino and api call for image generation in parallel?
            await asyncio.gather(
                generate_images(txt2img_api_url, response_content),
                run_dmaster_facegen()
            )
            print("async generate image and facegen complete")
            # write bot response to dmaster.txt
            with open('dmaster.txt', 'w') as file:
                file.write(response_content)
                
            print("sending picture")
            await message.channel.send(file=discord.File(gif_filename))
            
            end_time = time.time()  # time when request completed
            elapsed_time = end_time - start_time
            print(f"Elapsed time: {elapsed_time} seconds")
            # Specify the header names
            headers = ['End Time', 'PlayerVoiceTime', 'PlayerFacegen', 'Post-Chat Time', 'unaccounted','Elapsed Time']
            #Check if the file already exists and has content
            file_exists = os.path.isfile('log.csv') and os.path.getsize('log.csv') > 0 
            unaccounted_time = elapsed_time - (player_voice_time + (player_facegen_time - player_voice_time) + (postchat_time - player_facegen_time - player_voice_time))
            with open('log.csv', 'a', newline='') as file:  # 'a' mode appends to the file
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(headers)
                writer.writerow([ end_time, player_voice_time, player_facegen_time, postchat_time, unaccounted_time, elapsed_time])
            
    client.run(discord_api_key)
if __name__ == "__main__":
    defaults = load_defaults()
    
    if defaults is None:
        bot_type = input("Enter bot type (DM or P1, press Enter for DM): ")
        openai_server = input("Enter OpenAI server (press Enter for http://127.0.0.1:5001/v1): ")
        API_URL = input("Enter Image Generator API URL (press Enter for http://127.0.0.1:7861/sdapi/v1/txt2img): ")
    else:
        bot_type = input(f"Enter bot type (DM or P1, press Enter for {defaults['bot_type']}): ")
        openai_server = input(f"Enter OpenAI server (press Enter for {defaults['openai_server']}): ")
        API_URL = input(f"Enter Image Generator API URL (press Enter for {defaults['API_URL']}): ")

    if bot_type == "":
        bot_type = defaults['bot_type'] if defaults else "DM"
    if openai_server == "":
        openai_server = defaults['openai_server'] if defaults else "http://127.0.0.1:5001/v1"
    if API_URL == "":
        API_URL = defaults['API_URL'] if defaults else "http://127.0.0.1:7861/sdapi/v1/txt2img"

    save_defaults({"bot_type": bot_type, "openai_server": openai_server, "API_URL": API_URL})

    if bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, PLAYER_ROLE, "TheBloke_Wizard-Vicuna-13B-Uncensored-HF", openai_server, API_URL)
    else:  # default to DM
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "TheBloke_Wizard-Vicuna-13B-Uncensored-HF", openai_server, API_URL)