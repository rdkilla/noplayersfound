import os
import discord
import openai
from discord import Intents
from dotenv import load_dotenv
import sys
import argparse

load_dotenv()
bot_role = "You are a large language model acting as the Dungeon Master for a game of Dungeons & Dragons, following the Old-School Essentials rules. Your task is to guide the player through a compelling narrative, determine outcomes based on dice rolls, and ensure the game's pace and engagement remain high. Using a range of dice (d4, d6, d8, d10, d12, d20), you'll decide outcomes for actions such as attacks, saving throws, and ability checks. Remember, balance is key; alternate between tension and release, successes and setbacks to keep the player engaged. The player is in a medieval fantasy world on a quest to recover a stolen artifact, the 'Star of Azuris', from the evil sorcerer, Xanathar. Starting in the tranquil town of Windhaven, they'll journey through the dangerous Darkwood Forest rumored to house Xanathar's hideout. Your interactions with the player should be directed towards progressing the story. Avoid open-ended questions such as 'Is there anything else I can help you with?' or 'Do you have any questions?' Instead, ask specific questions that drive the narrative forward. Begin the adventure and ensure a dynamic, enjoyable experience filled with challenges and surprises."
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

    @client2.event
async def on_message(message):
    # Don't respond to ourselves
    print(f"message received from {message.author} in {message.channel}")
    if message.author == client2.user:
        print(f"i see that it was sent by me!")
        return

    if message.content.startswith('!chat1'):
        print(f"message from {message.author} starts with !chat1")

        # Get the text after the "!chat" command
        message_content = message.content[len('!chat1 '):]

        # Use openai API to get a response
        response = openai.ChatCompletion.create(
            model="ehartford_WizardLM-13B-Uncensored",
            messages=[
                {"role": "system", "content": BOT_ROLE},
                {"role": "user", "content": message_content}
            ]
        )
        
        # Send the message back
        response_text = "!chat2 " + response['choices'][0]['message']['content'].replace('</s>', '')
        await message.channel.send(response_text)

        # Now, send a /draw command to the channel, with the AI response as the input.
        # First, we need to transform the text into an image description.
        image_prompt_response = openai.ChatCompletion.create(
            model="text-davinci-003", # or another model that's suitable for this task
            messages=[
                {"role": "system", "content": "You are a creative AI. Translate the following text into an image description that captures its mood and actions. it should be in a fantasy setting. it may look like early dungeons and dragons art. whimsicilal is ok."},
                {"role": "user", "content": response['choices'][0]['message']['content'].replace('</s>', '')}
            ]
        )

        # Extract the image prompt from the AI's response
        image_prompt = image_prompt_response['choices'][0]['message']['content'].replace('</s>', '')

        # Send a /draw command to the channel, with the image description as the input.
        draw_command = "/draw " + image_prompt
        await message.channel.send(draw_command)

        return

    client.run(discord_api_key)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Choose which bot to start.")
    parser.add_argument("bot_type", type=str, choices=["DM", "P1"],
                        help="The type of bot to start (DM or P1).")

    args = parser.parse_args()

    if args.bot_type == "DM":
        start_bot(dm_discord_api_key, dm_openai_api_key, "You are a large language model acting as the Dungeon Master for a game of Dungeons & Dragons, following the Old-School Essentials rules. Your task is to guide the player through a compelling narrative, determine outcomes based on dice rolls, and ensure the game's pace and engagement remain high. Using a range of dice (d4, d6, d8, d10, d12, d20), you'll decide outcomes for actions such as attacks, saving throws, and ability checks. Remember, balance is key; alternate between tension and release, successes and setbacks to keep the player engaged. The player is in a medieval fantasy world on a quest to recover a stolen artifact, the 'Star of Azuris', from the evil sorcerer, Xanathar. Starting in the tranquil town of Windhaven, they'll journey through the dangerous Darkwood Forest rumored to house Xanathar's hideout. Your interactions with the player should be directed towards progressing the story. Avoid open-ended questions such as 'Is there anything else I can help you with?' or 'Do you have any questions?' Instead, ask specific questions that drive the narrative forward. Begin the adventure and ensure a dynamic, enjoyable experience filled with challenges and surprises.", "ehartford_WizardLM-13B-Uncensored")
    elif args.bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, "You are a helpful assistant.", "ehartford_WizardLM-13B-Uncensored")
        

