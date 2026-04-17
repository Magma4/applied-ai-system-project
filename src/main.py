"""
Command line runner for the Music Recommender Simulation.

Step 4 — CLI verification: from the project root, run::

    python -m src.main

Confirm: a line like ``Loaded songs: N`` (N matches your CSV), then the top
``k`` recommendations with scores and reason lines—proves ``load_songs``,
``score_song``, and ``recommend_songs`` work end-to-end.

Implements / uses in ``recommender.py``: ``load_songs``, ``score_song``,
``recommend_songs``.
"""

from typing import Any, Dict, List, Tuple

from src.recommender import load_songs, recommend_songs

# Terminal width for section rules (ASCII, works everywhere)
_OUT_WIDTH = 72


def _print_recommendations(
    recommendations: List[Tuple[Dict[str, Any], float, List[str]]],
) -> None:
    """Pretty-print ranked songs: title, final score, and scoring reasons."""
    rule = "=" * _OUT_WIDTH
    divider = "-" * _OUT_WIDTH

    print()
    print(rule)
    print("  TOP RECOMMENDATIONS")
    print(rule)

    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        print()
        print(f"  #{i}  {song['title']}")
        print(f"      Final score:  {score:.2f}")
        print("      Reasons:")
        for line in reasons:
            print(f"        · {line}")
        if i < len(recommendations):
            print()
            print(divider)

    print()
    print(rule)
    print()


def main() -> None:
    """CLI-first entrypoint: load CSV, rank for default prefs, print recommendations."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # Default taste profile: pop / happy (matches tests and common demo)
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    _print_recommendations(recommendations)


if __name__ == "__main__":
    main()
