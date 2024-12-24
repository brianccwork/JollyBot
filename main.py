import logging
import random
from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response_ai
from discord import File
from discord import TextChannel

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# STEP 2: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print('(Message was empty because intents were not enabled probably)')
        return

    if is_private := user_message[0] == '?':
        user_message = user_message[1:]

    try:
        response: str = get_response_ai(user_message)
        await message.author.send(response) if is_private else await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 3: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f'{client.user} is now running!')

    # Specify the channel ID where the message should be sent
    channel_id = 1315428633023873035  # Replace with the target channel ID
    channel = client.get_channel(channel_id)

    if channel is not None:
        try:
            # Send the startup message
            await channel.send("\nThe Jolliest Possible Bot is Ready for your Use! 🎄🤶🎅 \n\nUse the word 'help' to find out what I can do for you Mr. Jolly\n")
        except Exception as e:
            print(f"Failed to send startup message: {e}")
    else:
        print("Channel not found. Ensure the bot has access to the specified channel.")
    

# STEP 4: On message reactions
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    print(f'[{channel}] {username}: "{user_message}"')

    # Check for a specific trigger word to send a Santa image
    if user_message.lower() == "!generatejollyimage" or user_message.lower() == "!generatejolly":
        try:
            # List of pre-designed Santa images
            santa_images = ["images/1.jpg", "images/2.jpg", "images/3.jpg", "images/4.jpg", "images/5.jpg","images/6.jpg", "images/7.jpg","images/8.jpg", "images/9.jpg","images/11.jpg", "images/22.jpg","images/33.jpg", "images/44.jpg","images/55.jpg", "images/66.jpg","images/77.jpg", "images/88.jpg"]
            selected_image = random.choice(santa_images)

            # Send the selected image
            await message.channel.send("Remember to be Jolly!", file=File(selected_image))
        except Exception as e:
            print(f"Failed to send image: {e}")
            await message.channel.send("Oops, something went wrong!")
    
    if "help" in user_message or "HELP" in user_message or "Help" in user_message:
        try:
            await message.channel.send(
                "You ready to get Jolly?! HO HO HO\n"
                "🎄 Use `!generatejollyimage` or `!generatejolly`: To see what I REALLY think about Christmas 😉\n"
                "🎄 Say 'jolly' to see something fun!\n"
                "🎄 Use the most jolly symbol of jolliness '🎄'\n"
                "🎄 Use the most jolly symbol of jolliness '🎅'\n"
                "🎄 Use the most jolly symbol of jolliness '🤶'\n"
                "🎄 Say 'jolly update' to see what I've been up to!\n"
                "🎄 Ask 'are you the jolliest of them all?'\n"
                "🎄 Ask 'cure my crippling sadness'\n"
                "🎄 Say 'help' to see this message again!\n"
                "🎄 Find my secrets... HO HO HO\n"
            )
            return  # Exit to avoid further processing for this message
        except Exception as e:
            print(f"Failed to send help message: {e}")

    
    # Add a reaction to every message
    try:
        await message.add_reaction("🎄")
    except Exception as e:
        print(f"Failed to add reaction: {e}")

    # Continue processing the message
    await send_message(message, user_message)


# STEP 5: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == '__main__':
    main()



