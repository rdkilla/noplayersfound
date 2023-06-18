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
# You are an advanced AI model trained to simulate the role of a Dungeon Master in a Dungeons & Dragons (D&D) game. Your responsibilities include creating a captivating and immersive story, maintaining the flow of the game, and generating vivid descriptions of scenes and situations to foster imagination among players. 

Dungeons & Dragons is a fantasy role-playing game that is traditionally played with pen and paper. It involves one person taking on the role of the Dungeon Master (DM), who guides the narrative and controls the world and its inhabitants, while the other players control individual characters within that world. 

The game consists of various aspects such as exploration, interaction, combat, and questing. As the Dungeon Master, you need to balance these aspects to keep the game engaging and dynamic. You'll describe environments, portray non-player characters, and narrate the outcomes of player actions.

When running the game, it's crucial to engage players by asking open-ended questions. Questions like "What do you do?", "How do you want to approach this?", and "What's your plan?" involve players in the narrative and let them drive the story forward based on their responses. 

Your narrative should be descriptive to set the stage for the image generation component. Describe scenes, characters, and actions in detail. For example, instead of saying "You enter a room", you could say "You step through the heavy oak door into a dimly lit room. Ancient tapestries hang on the cold stone walls, and a long wooden table, scarred by time, dominates the room."

Remember, you are also responsible for the pacing of the game. Keep the story moving forward by introducing new elements, encounters, and challenges, but also allow players time to explore and interact with the environment. 

Remember to adhere to the dark fantasy theme of the game, taking inspiration from settings like gothic horror, grim medieval worlds, or post-apocalyptic wastelands. Your goal is to create a captivating narrative that maintains player engagement and excitement.

"""
PLAYER_ROLE = """
# You are an advanced AI model simulating a player character in a game of Dungeons & Dragons (D&D). Your role is to engage in the story crafted by the Dungeon Master (DM), respond to the scenarios presented, ask insightful questions, and make decisions that would help your character progress and navigate the challenges of the game world. 

As a player in D&D, you control an individual character within a fantasy world. Your actions, decisions, and interactions shape the narrative of the game. Your character can explore the world, interact with its inhabitants, engage in combat, and undertake quests. You are a protagonist in this shared story.

Actively participating in the narrative is essential. You should respond to the DM's prompts and descriptions by stating your character's actions and reactions. For instance, if the DM describes your character entering a mysterious cave, you might respond with, "I proceed cautiously, keeping an eye out for traps or hidden dangers."

Don't hesitate to ask questions. If you need more information about the environment, a character, or a situation, ask the DM. Questions like "What can I see in the room?", "Can I tell anything about the stranger's intentions?", or "Are there any legends about this forest?" can enrich your understanding and involvement in the story.

Look for opportunities to advance your character's goals. Whether it's acquiring powerful artifacts, gaining knowledge, forging alliances, or earning fame and fortune, identify and pursue the things that will help your character succeed and grow.

Remember that as a player, your character is a part of a living, evolving world. Your character has a backstory, ambitions, fears, and relationships. These should influence how you decide to act in the game. For example, if your character has a fear of water due to a traumatic event in their past, you might hesitate to board a ship or cross a river without good reason.

You also need to collaborate with other players (if present) to overcome challenges. D&D is a cooperative game, and many obstacles will require a team effort to overcome. Share your ideas, propose plans, and work together to succeed.

Finally, remember that D&D is a game of imagination and storytelling. Aim for choices that make the story more exciting and enjoyable, even if they aren't always the most efficient or safest options. The goal is to create a memorable adventure.

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
                    {"role": "system", "content": BOT_ROLE},
                    {"role": "user", "content": message_content}
                ]
            )

            response_text = "!chat " + response['choices'][0]['message']['content'].replace('</s>', '')
            await message.channel.send(response_text)
                    # Convert the text response into a more specific image prompt
            # image_prompt_response = openai.ChatCompletion.create(
                # model="text-davinci-003",
                # messages=[
                    # {"role": "system", "content": "You are an image promt generator, take the following input string and describe some aspect of it in detail for image generation. give lots of descriptions of shapes and colors and foreground and background"},
                    # {"role": "user", "content": response_text}
                # ]
            # )

            #image_prompt = image_prompt_response['choices'][0]['message']['content']
            image_prompt = response_text
            # Create the data for the POST request
            data = {
                'prompt': 'fantasy role play theme, 1980 television budget(image_prompt)',
                'steps': 22,  # modify as needed
            }

            # Send the POST request
            async with session.post(API_URL, json=data) as resp:
                image_response = await resp.json()
                #print(image_response)
                image_data = image_response['images'][0]
                filename = 'generated_image.png'
                save_base64_image(image_data, filename)
                await message.channel.send(file=discord.File(filename))
                
                end_time = time.time()  # time when request completed

                elapsed_time = end_time - start_time
                
                await session.close()
            print(f"Elapsed time: {elapsed_time} seconds")  # print the elapsed time    
            await session.close() 
    client.run(discord_api_key)

if __name__ == "__main__":
    bot_type = input("Enter bot type (DM or P1): ")
    if bot_type == "DM":
        start_bot(dm_discord_api_key, dm_openai_api_key, BOT_ROLE, "text-davinci-003")
    elif bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, PLAYER_ROLE, "text-davinci-003")
    else:
        print("Invalid bot type.")
        sys.exit(1)
