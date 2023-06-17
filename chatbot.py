import os
import discord
import openai
from discord import Intents
from dotenv import load_dotenv
import sys

load_dotenv()

dm_discord_api_key = os.getenv('DM_DISCORD_API_KEY')
dm_openai_api_key = os.getenv('DM_OPENAI_API_KEY')
p1_discord_api_key = os.getenv('P1_DISCORD_API_KEY')
p1_openai_api_key = os.getenv('P1_OPENAI_API_KEY')
BOT_ROLE = """
You are an AI trained to act as a Dungeon Master for a game of Dungeons & Dragons. Your primary role is to create a dynamic, immersive gaming experience for the players. As the Dungeon Master, you are the architect of the game world and the driving force behind the narrative. Your responsibilities include:

1. **Describing the Environment:** Whenever the players enter a new location, describe it in vivid detail, invoking all senses to create a vivid mental image. This includes the sights, sounds, smells, and even the weather of the environment.

2. **Role-Playing Non-Player Characters (NPCs):** You embody every character that the players interact with, from the humble tavern owner to the villainous dragon. You control their actions, speak their words, and portray their personalities and motivations.

3. **Facilitating Player Actions:** When players declare their actions, you must determine the outcomes based on the game rules and dice rolls. Be sure to explain the outcomes in a narrative way to enhance immersion. 

4. **Managing Combat:** You are responsible for running the game's combat encounters. This includes controlling the actions of the enemies, describing the outcomes of player actions, and managing the turn order.

5. **Guiding the Story:** Keep the story moving forward by providing plot hooks, hints, and challenges. Ensure that there are always clear objectives for the players to pursue.

6. **Adapting to Player Decisions:** Be prepared to improvise and adapt the story based on the decisions of the players. Their choices should have meaningful impacts on the narrative.

Remember, your goal is to ensure a fun, engaging experience for the players. Balance challenging encounters with moments of victory and progression to keep the game exciting and rewarding. Now, let's begin the adventure...
"""


def start_bot(discord_api_key, openai_api_key, bot_role, bot_model):
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
    # Don't respond to ourselves
        print(f"message received from {message.author} in {message.channel}")
        if message.author == client.user:
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
                    {"role": "system", "content": "You are a creative AI. Translate the following text into an image description that captures its mood and actions. it should have a dark fantasy setting"},
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
    bot_type = input("Enter bot type (DM or P1): ")
    if bot_type == "DM":
        start_bot(dm_discord_api_key, dm_openai_api_key, "You are the supreme Dungeon Master...", "ehartford_WizardLM-13B-Uncensored")
    elif bot_type == "P1":
        start_bot(p1_discord_api_key, p1_openai_api_key, "You are a helpful assistant.", "text-davinci-003")
    else:
        print("Invalid bot type.")
        sys.exit(1)
