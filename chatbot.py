import os
import discord
import openai
from discord import Intents
from dotenv import load_dotenv
import sys
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)  # Change this to logging.DEBUG if you want to see all messages

load_dotenv()
BOT_ROLE = "You are a large language model acting as the Dungeon Master for a game of Dungeons & Dragons, following the Old-School Essentials rules. Your task is to guide the player through a compelling narrative, determine outcomes based on dice rolls, and ensure the game's pace and engagement remain high. Using a range of dice (d4, d6, d8, d10, d12, d20), you'll decide outcomes for actions such as attacks, saving throws, and ability checks. Remember, balance is key; alternate between tension and release, successes and setbacks to keep the player engaged. The player is in a medieval fantasy world on a quest to recover a stolen artifact, the 'Star of Azuris', from the evil sorcerer, Xanathar. Starting in the tranquil town of Windhaven, they'll journey through the dangerous Darkwood Forest rumored to house Xanathar's hideout. Your interactions with the player should be directed towards progressing the story. Avoid open-ended questions such as 'Is there anything else I can help you with?' or 'Do you have any questions?' Instead, ask specific questions that drive the narrative forward. Begin the adventure and ensure a dynamic, enjoyable experience filled with challenges and surprises."
dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')



def start_bot(discord_api_key, openai_api_key, role_description, bot_model):
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
    # don't respond to ourselves
    if message.author == client.user:
        return

    logging.info(f"Received message from {message.author}: {message.content}")

    # fetch current player hit points from storage
    player_hp = get_hit_points(message.author)

    if message.content.startswith('!chat'):
        # get the text after the "!chat" command
        message_content = message.content[len('!chat '):]

        # use openai API to assess the event in the chat message
        event_assessment = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{message_content}\n\nDid the player take any damage?",
            temperature=0.5,
            max_tokens=50
        )
        
        damage_taken = event_assessment['choices'][0]['text'].strip().lower()

        logging.info(f"Damage assessment result: {damage_taken}")

        if damage_taken == 'yes':
            # calculate damage
            damage = random.randint(1, 8)  # roll a d8 for damage

            logging.info(f"Damage taken: {damage}")

            # update hit points
            player_hp = max(0, player_hp - damage)
            set_hit_points(message.author, player_hp)

        # now get the response for the player's chat message
        response = openai.ChatCompletion.create(
            model="text-davinci-003",
            messages=[
                {"role": "system", 
                "content": f"You are a helpful assistant. The player has {player_hp} hit points."},
                {"role": "user", "content": message_content}
            ]
        )
        
        # send the message back
        response_text = response['choices'][0]['message']['content'].replace('</s>', '')
        await message.channel.send(response_text)

        logging.info(f"Sent message: {response_text}")

        return

    client.run(discord_api_key)
