# main.py
import logging
import random
import os
from typing import Final
from datetime import datetime, time as dtime

from dotenv import load_dotenv
from discord import Intents, Client, Message, File
from discord.ext import tasks

from responses import get_response, get_random_jolly
from scores import add_jolly_points, format_leaderboard, get_user_score
from advent import get_advent_message
from data_loader import load_json

# STEP 0: LOAD OUR TOKEN FROM SOMEWHERE SAFE
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")

# Channel where startup + daily messages + holiday pings go
ANNOUNCEMENT_CHANNEL_ID: Final[int] = 1440361844471758999  # change if needed

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

logging.basicConfig(level=logging.INFO)

# Images for !generatejolly / !generatejollyimage and advent
SANTA_IMAGES = load_json("santa_images.json")

# December multi-tradition holiday events loaded from JSON.
# JSON keys are "MM-DD" -> message, we convert to (month, day) -> message
_raw_holiday_events = load_json("holiday_events.json")
HOLIDAY_EVENTS: dict[tuple[int, int], str] = {}

for key, msg in _raw_holiday_events.items():
    month_str, day_str = key.split("-")
    HOLIDAY_EVENTS[(int(month_str), int(day_str))] = msg


# STEP 2: DAILY JOLLY / ADVENT / LEADERBOARD TASK
@tasks.loop(time=dtime(hour=0, minute=0))
async def send_daily_jolly_message():
    """
    Runs daily at ~00:00 (server time).
    - Sends holiday pings if applicable
    - Sends Advent message with image (Dec 1–25) OR a jolly image on other days
    - Shows Jolly leaderboard each day of December
    """
    await client.wait_until_ready()

    channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if channel is None:
        logging.warning(
            "Announcement channel not found. Check ANNOUNCEMENT_CHANNEL_ID and bot permissions."
        )
        return

    now = datetime.now()
    date_key = (now.month, now.day)

    # 1) Special holiday ping (December, multi-religion friendly, etc.)
    holiday_msg = HOLIDAY_EVENTS.get(date_key)
    if holiday_msg:
        try:
            await channel.send(f"@everyone {holiday_msg}")
        except Exception as e:
            logging.error(f"Failed to send holiday message: {e}")

    # 2) Advent calendar (Dec 1–25) OR general jolly image
    try:
        selected_image = random.choice(SANTA_IMAGES)

        if now.month == 12 and 1 <= now.day <= 25:
            advent_text = get_advent_message(now.day)
            if advent_text is None:
                advent_text = f"Day {now.day}: Be extra jolly today! {get_random_jolly()}"

            advent_header = f"🎁 **Jolly Advent Calendar – Day {now.day}** 🎁"
            await channel.send(
                f"{advent_header}\n{advent_text}",
                file=File(selected_image),
            )
        else:
            # Outside Advent: just drop a jolly image + phrase once per day
            jolly_line = get_random_jolly()
            await channel.send(
                f"🎄 **Daily Jolly Image** 🎄\n{jolly_line}",
                file=File(selected_image),
            )
    except Exception as e:
        logging.error(f"Failed to send daily image/advent message: {e}")

    # 3) Jolly leaderboard (each day of December)
    if now.month == 12:
        try:
            leaderboard_text = format_leaderboard(top_n=5)
            await channel.send(
                "🏆 **Jolly Leaderboard – Top 5** 🏆\n" + leaderboard_text
            )
        except Exception as e:
            logging.error(f"Failed to send leaderboard: {e}")


# STEP 3: MESSAGE FUNCTIONALITY
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("(Message was empty because intents were not enabled probably)")
        return

    # Still support ?prefix to DM instead of replying in channel
    is_private = user_message.startswith("?")
    if is_private:
        user_message = user_message[1:]

    try:
        response = get_response(user_message)
        if response is None:
            # No specific JollyBot reply; we only reacted with 🎄 in on_message
            return

        if is_private:
            await message.author.send(response)
        else:
            await message.channel.send(response)
    except Exception as e:
        print(e)


# STEP 4: HANDLING THE STARTUP FOR OUR BOT
@client.event
async def on_ready() -> None:
    print(f"{client.user} is now running!")

    channel = client.get_channel(ANNOUNCEMENT_CHANNEL_ID)

    if channel is not None:
        try:
            await channel.send(
                "\nThe Jolliest Possible Bot is Ready for your Use! 🎄🤶🎅 \n\n"
                "Use the word 'help' to find out what I can do for you, Mr. Jolly\n"
            )
        except Exception as e:
            print(f"Failed to send startup message: {e}")
    else:
        print("Channel not found. Ensure the bot has access to the specified channel.")

    # Start the daily jolly task once the bot is ready
    if not send_daily_jolly_message.is_running():
        send_daily_jolly_message.start()


# STEP 5: On message reactions / commands
@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return

    username: str = str(message.author)
    user_message: str = message.content
    channel_name: str = str(message.channel)

    print(f'[{channel_name}] {username}: "{user_message}"')

    lowered = user_message.lower()

    # --- JollyScore system: any interaction with JollyBot = +1 point ---
    try:
        interacted = False

        # Exact "jolly"
        if lowered.strip() == "jolly":
            interacted = True

        # Festive emojis
        if "🎄" in user_message or "🎅" in user_message or "🤶" in user_message:
            interacted = True

        # Commands
        if lowered.startswith("!advent"):
            interacted = True
        if lowered.startswith("!jollyscore"):
            interacted = True
        if lowered.startswith("!generatejollyimage") or lowered.startswith("!generatejolly"):
            interacted = True

        # Help (since it triggers a JollyBot reply)
        if "help" in user_message or "HELP" in user_message or "Help" in user_message:
            interacted = True

        # If it triggered *anything* JollyBot responds to, add 1 point.
        if interacted:
            add_jolly_points(message.author.id, message.author.display_name, points=1)
    except Exception as e:
        print(f"Failed to update jolly score: {e}")

    # --- !jollyscore command ---
    if lowered.startswith("!jollyscore"):
        try:
            leaderboard_text = format_leaderboard(top_n=5)
            user_score = get_user_score(message.author.id)
            await message.channel.send(
                "🏆 **Jolly Leaderboard – Top 5** 🏆\n"
                f"{leaderboard_text}\n\n"
                f"🎄 {message.author.display_name}, you have **{user_score}** "
                f"jolly point{'s' if user_score != 1 else ''}!"
            )
        except Exception as e:
            print(f"Failed to send jollyscore: {e}")

        try:
            await message.add_reaction("🎄")
        except Exception as e:
            print(f"Failed to add reaction: {e}")
        return

    # --- !advent command ---
    if lowered.startswith("!advent"):
        now = datetime.now()
        if now.month == 12 and 1 <= now.day <= 25:
            try:
                advent_text = get_advent_message(now.day)
                if advent_text is None:
                    advent_text = f"Day {now.day}: Be extra jolly today! {get_random_jolly()}"

                header = f"🎁 **Jolly Advent Calendar – Day {now.day}** 🎁"
                selected_image = random.choice(SANTA_IMAGES)
                await message.channel.send(
                    f"{header}\n{advent_text}",
                    file=File(selected_image),
                )
            except Exception as e:
                print(f"Failed to send advent command: {e}")
        else:
            await message.channel.send(
                "The Jolly Advent Calendar runs from December 1st to 25th. "
                "But you can still be jolly today! 🎄"
            )

        try:
            await message.add_reaction("🎄")
        except Exception as e:
            print(f"Failed to add reaction: {e}")
        return

    # --- Image generator command ---
    if lowered == "!generatejollyimage" or lowered == "!generatejolly":
        try:
            selected_image = random.choice(SANTA_IMAGES)
            await message.channel.send("Remember to be Jolly!", file=File(selected_image))
        except Exception as e:
            print(f"Failed to send image: {e}")
            await message.channel.send("Oops, something went wrong!")
        # Still add reaction, then return to avoid double-handling
        try:
            await message.add_reaction("🎄")
        except Exception as e:
            print(f"Failed to add reaction: {e}")
        return

    # --- Help text trigger ---
    if "help" in user_message or "HELP" in user_message or "Help" in user_message:
        try:
            await message.channel.send(
                "You ready to get Jolly?! HO HO HO\n"
                "🎄 Use `!generatejollyimage` or `!generatejolly`: To see what I REALLY think about Christmas 😉\n"
                "🎄 Say `jolly` to see something fun (and earn Jolly points)!\n"
                "🎄 Use the most jolly symbol of jolliness `🎄`, `🎅`, `🤶` (they also earn Jolly points!)\n"
                "🎄 Say `jolly update` to see what I've been up to!\n"
                "🎄 Ask `are you the jolliest of them all?`\n"
                "🎄 Ask `cure my crippling sadness`\n"
                "🎄 Say `help` to see this message again!\n"
                "🎄 Use `!advent` for today’s Advent Calendar gift (Dec 1–25)!\n"
                "🎄 Use `!jollyscore` to see the Jolly leaderboard & your score!\n"
                "🎄 Find my secrets... HO HO HO\n"
            )
        except Exception as e:
            print(f"Failed to send help message: {e}")

        # Add reaction and stop here
        try:
            await message.add_reaction("🎄")
        except Exception as e:
            print(f"Failed to add reaction: {e}")
        return

    # --- Add a 🎄 reaction to every message ---
    try:
        await message.add_reaction("🎄")
    except Exception as e:
        print(f"Failed to add reaction: {e}")

    # --- Let the Jolly response handler run (elif chain) ---
    await send_message(message, user_message)


# STEP 6: MAIN ENTRY POINT
def main() -> None:
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
