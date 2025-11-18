# responses.py
import random
from typing import List

from data_loader import load_json

# All jolly phrases come from data/jolly_phrases.json
JOLLY_PHRASES: List[str] = load_json("jolly_phrases.json")


def get_random_jolly() -> str:
    return random.choice(JOLLY_PHRASES)


def get_response(user_input: str) -> str | None:
    lowered = user_input.lower().strip()

    # Main trigger: jolly
    if lowered == "jolly":
        return get_random_jolly()

    # Merry Christmas variants
    elif lowered in {
        "merry christmas",
        "merry christmas!",
        "merry christmas.",
    }:
        return "Merry Christmas to you too! 🎄"

    # Emojis / fun triggers
    elif lowered == "🎄":
        return "Ugly ass tree bro 🎄"
    elif lowered == "🎅":
        return "the big man himself"
    elif lowered == "🤶":
        return "she is quite jolly I would say myself"
    elif lowered == "😉":
        return "I see you ARE getting quite jolly... HO HO HO"

    # Phrases
    elif lowered == "cure my crippling sadness":
        return "Whenever darkness is near just remember to be jolly!"
    elif lowered == "jolly update":
        return "Yup I updated... again..."
    elif lowered in {"are you the jolliest", "are you the jolliest?"}:
        return "Only the jolliest of them all"
    elif lowered in {
        "are you the jolliest of them all",
        "are you the jolliest of them all?",
    }:
        return "Only the jolliest of them all"
    elif lowered in {
        "what do you think of christmas?",
        "what do you think of christmas",
    }:
        return "Only the jolliest of all the Seasons my friend... HO HO HO"
    elif lowered == "hohoho":
        return "Only the jolliest know this saying!"
    elif lowered == "ho ho ho":
        return "I can see you being super jolly!"
    elif lowered == "ho":
        return "You are almost jolly!!!"
    elif lowered == "rudolph":
        return "An old friend of mine..."

    # No known trigger -> let the bot just react with 🎄 but not send text
    return None
