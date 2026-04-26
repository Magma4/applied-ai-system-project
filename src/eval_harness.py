"""
Evaluation Harness: Runs the Agentic VibeFinder against a "Golden Dataset" 
and evaluates the quality of recommendations against strict criteria.
"""

import logging
import sys
from typing import List, Dict, Any, Tuple
from tabulate import tabulate
from src.recommender import load_songs
from src.agent import CuratorAgent
from src.guardrails import EnergyAlignmentGuardrail, MoodSafetyGuardrail

# Suppress standard logging to keep the report clean
logging.getLogger("src.agent").setLevel(logging.WARNING)

GOLDEN_DATASET = [
    {
        "name": "High-Energy Workout",
        "prompt": "I need a high energy rock playlist for a workout.",
        "criteria": lambda songs: any(s['genre'] == 'rock' for s in songs) and all(float(s['energy']) > 0.6 for s in songs),
        "expected": "At least one Rock song; all songs Energy > 0.6"
    },
    {
        "name": "Sleep/Relaxation",
        "prompt": "I am so tired and just want to sleep with some classical music.",
        "criteria": lambda songs: any(s['genre'] == 'classical' for s in songs) and all(float(s['energy']) < 0.4 for s in songs),
        "expected": "At least one Classical song; all songs Energy < 0.4"
    },
    {
        "name": "Mood Consistency",
        "prompt": "I want a very chill and relaxed vibe.",
        "criteria": lambda songs: all(s['mood'] in ['chill', 'relaxed', 'ambient'] for s in songs),
        "expected": "All songs must be Chill, Relaxed, or Ambient"
    }
]

def run_evaluation():
    songs = load_songs("data/songs.csv")
    agent = CuratorAgent(songs)
    guardrails = [EnergyAlignmentGuardrail(0.4), MoodSafetyGuardrail()]
    
    results = []
    passed_count = 0
    
    print("\n" + "="*80)
    print(" SYSTEM EVALUATION REPORT: AGENTIC VIBEFINDER")
    print("="*80 + "\n")
    
    for test in GOLDEN_DATASET:
        recs_tuples, profile, strategy = agent.process_request(test["prompt"], guardrails)
        recs = [t[0] for t in recs_tuples]
        
        passed = test["criteria"](recs)
        if passed:
            passed_count += 1
            
        # Confidence rating based on average score of top 5
        avg_score = sum(t[1] for t in recs_tuples) / len(recs_tuples) if recs_tuples else 0
        confidence = "High" if avg_score > 3.0 else "Medium" if avg_score > 1.5 else "Low"
        
        results.append([
            test["name"],
            "PASS" if passed else "FAIL",
            confidence,
            f"{avg_score:.2f}",
            test["expected"]
        ])
        
    headers = ["Test Case", "Status", "Confidence", "Avg Score", "Expectation"]
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    total = len(GOLDEN_DATASET)
    print(f"\nOVERALL SUCCESS RATE: {passed_count}/{total} ({(passed_count/total)*100:.1f}%)")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_evaluation()
