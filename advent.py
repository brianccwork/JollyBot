# advent.py
from typing import Dict

from data_loader import load_json

# All advent messages come from data/advent_messages.json
_ADVENT_MESSAGES: Dict[str, str] = load_json("advent_messages.json")


def get_advent_message(day: int) -> str | None:
# Return the advent message for the given day, or None if not found.
    return _ADVENT_MESSAGES.get(str(day))
