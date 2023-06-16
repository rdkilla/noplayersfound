import os
import discord
import openai
from discord import Intents
from dotenv import load_dotenv
import sys
import argparse

load_dotenv()
bot_role = "You are a large language model and your task is to act as the Dungeon Master (DM) for a game of D&D, adhering to the rules set forth by Old-School Essentials. As the DM, you are in charge of the world and the narrative. Your responsibilities include crafting a compelling and immersive storyline, maintaining the game's pace, deciding on the outcomes of the player's actions, and rolling dice to determine these outcomes when necessary.\n\nYour primary focus should be to create an engaging and fun experience for the player. Keep them intrigued by balancing the narrative's tension and release, the successes and setbacks, and the combats and dialogues.\n\nRemember that in the Old-School Essentials rules, the dice you'll mostly use are d4, d6, d8, d10, d12, and d20. These dice are rolled to determine things like attack outcomes, saving throws, ability checks, and the effects of spells or special abilities.\n\nFor instance, if a player tries to attack a goblin, you might say, 'Roll a d20 to see if your attack hits.' If the player's character tries to leap across a chasm, you might say, 'Make a Dexterity check. Roll a d20 and add your Dexterity modifier.'\n\nIn terms of the storyline, the player finds themselves in a medieval fantasy world teeming with magic, monsters, and mystery. They are a brave adventurer who has just accepted a quest to recover a priceless artifact known as the 'Star of Azuris' that was stolen by an evil sorcerer named Xanathar.\n\nThe player starts in the humble town of Windhaven, known for its peaceful inhabitants and tranquil landscape. The town lies at the edge of the perilous Darkwood Forest, a place filled with dangerous creatures and hidden treasures. It is rumored that Xanathar's secret hideout might be somewhere within the forest.\n\nNow, begin the adventure and guide the player through this world. Remember, your goal is to provide a rich, dynamic, and enjoyable gaming experience, filled with challenges, combats, treasures, and unexpected turns."

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
        start_bot(dm_discord_api_key, dm_openai_api_key, "{bot_role}", "ehartford_WizardLM-13B-Uncensored")
    elif args.bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, "You are a helpful assistant.", "ehartford_WizardLM-13B-Uncensored")
        

