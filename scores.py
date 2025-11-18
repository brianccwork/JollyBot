# scores.py
import json
import os
from typing import Dict, List, Tuple

SCORES_FILE = "data/jolly_scores.json"


def _load_scores() -> Dict[str, dict]:
    #loads scores from disk.
    if not os.path.exists(SCORES_FILE):
        return {}
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_scores(scores: Dict[str, dict]) -> None:
    #saves scores to disk.
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except Exception as e:
        print(f"Failed to save jolly scores: {e}")


def add_jolly_points(user_id: int, username: str, points: int = 1) -> None:

    #Increment a user's jolly score.
    #user_id is stored as string; username is kept as a display label.

    scores = _load_scores()
    key = str(user_id)

    if key not in scores:
        scores[key] = {"name": username, "score": 0}

    # Keep latest display name
    scores[key]["name"] = username
    scores[key]["score"] = int(scores[key].get("score", 0)) + points

    _save_scores(scores)


def get_sorted_scores() -> List[Tuple[str, dict]]:
    #Return scores sorted descending by jolly points.
    scores = _load_scores()
    return sorted(scores.items(), key=lambda item: item[1].get("score", 0), reverse=True)


def format_leaderboard(top_n: int = 5) -> str:
    #Return a Discord-friendly leaderboard text.
    sorted_scores = get_sorted_scores()
    if not sorted_scores:
        return (
            "No jolly points yet. Start saying `jolly`, using 🎄, 🎅, 🤶, "
            "or running jolly commands to climb the board!"
        )

    lines = []
    for rank, (user_id, data) in enumerate(sorted_scores[:top_n], start=1):
        name = data.get("name", f"User {user_id}")
        score = int(data.get("score", 0))
        lines.append(f"{rank}. **{name}** – {score} jolly point{'s' if score != 1 else ''}")
    return "\n".join(lines)


def get_user_score(user_id: int) -> int:
    #Get a specific user's jolly score.
    scores = _load_scores()
    data = scores.get(str(user_id))
    if not data:
        return 0
    try:
        return int(data.get("score", 0))
    except Exception:
        return 0
