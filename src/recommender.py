from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

# Finalized linear score: genre and mood are binary; energy adds up to 1.0 similarity.
W_GENRE = 2.0
W_MOOD = 1.0


def _norm(s: str) -> str:
    """Normalize a label string for case-insensitive comparison."""
    return str(s).strip().casefold()


def energy_similarity(song_energy: float, target_energy: float) -> float:
    """Energy closeness in [0, 1] from absolute difference to target on [0, 1]."""
    return max(0.0, min(1.0, 1.0 - abs(float(song_energy) - float(target_energy))))


def compute_score_and_reasons(
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    genre: str,
    mood: str,
    energy: float,
) -> Tuple[float, List[str]]:
    """Compute total score plus reason strings for genre, mood, and energy fit."""
    reasons: List[str] = []
    total = 0.0
    if _norm(genre) == _norm(favorite_genre):
        total += W_GENRE
        reasons.append(f"genre match (+{W_GENRE:.1f})")
    if _norm(mood) == _norm(favorite_mood):
        total += W_MOOD
        reasons.append(f"mood match (+{W_MOOD:.1f})")
    e = energy_similarity(energy, target_energy)
    total += e
    reasons.append(
        f"energy fit (+{e:.2f}); song energy {float(energy):.2f} vs target {float(target_energy):.2f}"
    )
    return total, reasons


def compute_score(
    favorite_genre: str,
    favorite_mood: str,
    target_energy: float,
    genre: str,
    mood: str,
    energy: float,
) -> float:
    """Return only the numeric total score for one song vs user targets."""
    return compute_score_and_reasons(
        favorite_genre,
        favorite_mood,
        target_energy,
        genre,
        mood,
        energy,
    )[0]


def score_song(user_prefs: Dict[str, Any], song: Dict[str, Any]) -> Tuple[float, List[str]]:
    """Return (score, reasons) for one catalog dict using the same rule as Recommender."""
    return compute_score_and_reasons(
        str(user_prefs["favorite_genre"]),
        str(user_prefs["favorite_mood"]),
        float(user_prefs["target_energy"]),
        str(song["genre"]),
        str(song["mood"]),
        float(song["energy"]),
    )


@dataclass
class Song:
    """One song with metadata and simulated audio feature columns."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """User taste profile: favorite genre/mood, target energy, acoustic flag."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Object-oriented wrapper: rank Song instances with the shared scoring rule."""
    def __init__(self, songs: List[Song]):
        """Store the in-memory catalog."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to k songs sorted by descending score, ties by id."""
        scored = [
            (
                compute_score(
                    user.favorite_genre,
                    user.favorite_mood,
                    user.target_energy,
                    s.genre,
                    s.mood,
                    s.energy,
                ),
                s.id,
                s,
            )
            for s in self.songs
        ]
        scored.sort(key=lambda t: (-t[0], t[1]))
        return [t[2] for t in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a single string joining all scoring reasons for one song."""
        _, reasons = compute_score_and_reasons(
            user.favorite_genre,
            user.favorite_mood,
            user.target_energy,
            song.genre,
            song.mood,
            song.energy,
        )
        return "; ".join(reasons)


def load_songs(csv_path: str) -> List[Dict[str, Any]]:
    """Read songs CSV into dicts with int id and float audio fields."""
    rows: List[Dict[str, Any]] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return rows


def recommend_songs(
    user_prefs: Dict[str, Any], songs: List[Dict[str, Any]], k: int = 5
) -> List[Tuple[Dict[str, Any], float, List[str]]]:
    """Score every dict in songs, sort descending by score, return top k tuples."""
    scored: List[Tuple[float, int, Dict[str, Any], List[str]]] = []
    for s in songs:
        score, reasons = score_song(user_prefs, s)
        scored.append((score, int(s["id"]), s, reasons))
    scored.sort(key=lambda t: (-t[0], t[1]))
    return [(t[2], t[0], t[3]) for t in scored[:k]]
