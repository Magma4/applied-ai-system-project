"""
Music Recommender CLI: Agentic Workflow with Guardrails.

Run from repo root::

    python -m src.main
"""

import os
import sys
import logging
from typing import Any, Dict, List, Tuple

from tabulate import tabulate

from src.recommender import load_songs
from src.agent import CuratorAgent
from src.guardrails import EnergyAlignmentGuardrail, MoodSafetyGuardrail

_OUT_WIDTH = 72

# Setup Logging
# We log to both a file and standard error (so it doesn't mess up our stdout tables)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/agent_reasoning.log"),
        logging.StreamHandler(sys.stderr)
    ]
)

AGENT_PROMPTS = [
    "I'm feeling pumped and need a high energy pop workout track.",
    "I'm tired and want to focus, maybe some acoustic lofi.",
    "I am very relaxed and just want to sleep, play some classical.",
    "Adversarial: I am very relaxed but I want intense rock." # Should trigger guardrail or be handled
]


def _print_agent_section(query: str) -> None:
    """Print a labeled block for one user prompt."""
    banner = "=" * _OUT_WIDTH
    print(f"\n{banner}")
    print(f"  USER PROMPT: {query!r}")
    print(banner)


def _print_recommendations_table(
    recommendations: List[Tuple[Dict[str, Any], float, List[str]]],
) -> None:
    """Tabular output including concatenated reasons."""
    if not recommendations:
        print("  [!] No recommendations passed the guardrails.")
        return
        
    rows = []
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        reasons_cell = " \n".join(reasons)
        rows.append(
            [
                i,
                song.get("title", ""),
                song.get("artist", ""),
                song.get("genre", ""),
                f"{score:.2f}",
                reasons_cell,
            ]
        )
    headers = ["#", "Title", "Artist", "Genre", "Score", "Reasons (scoring)"]
    print(tabulate(rows, headers=headers, tablefmt="grid", stralign="left"))


def main() -> None:
    """Run the Agentic Workflow against a set of natural language prompts."""
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print("Check logs/agent_reasoning.log for detailed agent decision making.")
    
    # Initialize Agent and Guardrails
    agent = CuratorAgent(catalog=songs)
    guardrails = [
        EnergyAlignmentGuardrail(max_variance=0.4),
        MoodSafetyGuardrail()
    ]

    for query in AGENT_PROMPTS:
        _print_agent_section(query)
        
        # The Agentic Plan -> Act -> Check loop
        recommendations, profile, strategy = agent.process_request(query, guardrails=guardrails)
        
        print(f"\n  [Agent Parsed Profile] Genre: {profile.favorite_genre}, Mood: {profile.favorite_mood}, Energy: {profile.target_energy}")
        print(f"  [Agent Strategy Selected] {strategy}\n")
        
        _print_recommendations_table(recommendations)
        print()


if __name__ == "__main__":
    main()
