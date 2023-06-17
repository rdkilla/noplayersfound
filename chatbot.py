import os
import time
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

BOT_ROLE = """
# I'm the dungeon master in a game of dnd
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
        if message.author == client.user:
            return
        session = aiohttp.ClientSession()
        if message.content.startswith('!chat'):
            start_time = time.time()  # time when request started
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

            # Convert the text response into a more specific image prompt
            image_prompt_response = openai.ChatCompletion.create(
                model="text-davinci-003",
                messages=[
                    {"role": "system", "content": "You are an image promt generator, take the following input string and describe some aspect of it in detail for image generation. give lots of descriptions of shapes and colors and foreground and background"},
                    {"role": "user", "content": response_text}
                ]
            )

            image_prompt = image_prompt_response['choices'][0]['message']['content']

            # Create the data for the POST request
            data = {
                'input': image_prompt,
                'steps': 20,  # modify as needed
            }

            # Send the POST request
            async with session.post(API_URL, json=data) as resp:
                image_response = await resp.json()
                #print(image_response)
                image_data = image_response['images'][0]
                filename = 'generated_image.png'
                save_base64_image(image_data, filename)
                await message.channel.send(file=discord.File(filename))
                await session.close() 
                end_time = time.time()  # time when request completed

                elapsed_time = end_time - start_time
                print(f"Elapsed time: {elapsed_time} seconds")  # print the elapsed time
    client.run(discord_api_key)

if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1): ")
    if bot_type == "DM":
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "text-davinci-003")
    elif bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, "You are a helpful assistant.", "text-davinci-003")
    else:
        print("Invalid bot type.")
        sys.exit(1)
