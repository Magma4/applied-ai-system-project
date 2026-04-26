import re
import logging
from typing import Dict, Any, List, Tuple
from src.recommender import UserProfile, recommend_songs, get_strategy_weights

logger = logging.getLogger(__name__)

class CuratorAgent:
    """
    Agent responsible for parsing natural language into user intents, 
    selecting scoring strategies, and refining recommendations.
    """
    
    def __init__(self, catalog: List[Dict[str, Any]]):
        self.catalog = catalog

    def parse_intent(self, query: str) -> UserProfile:
        """
        Parses a natural language query into a structured UserProfile.
        This uses rule-based parsing to act deterministically.
        """
        query_lower = query.lower()
        logger.info(f"[Agent] Parsing intent for query: '{query}'")
        
        # Default baseline
        genre = "pop"
        mood = "happy"
        energy = 0.5
        likes_acoustic = False

        # 1. Parse Genre
        genres = ["pop", "rock", "lofi", "classical", "jazz", "hip hop", "electronic"]
        for g in genres:
            if g in query_lower:
                genre = g
                logger.debug(f"  -> Found genre intent: {g}")
                break
                
        # 2. Parse Mood
        moods = ["happy", "chill", "intense", "somber", "melancholic", "relaxed", "focus", "sad", "upbeat"]
        for m in moods:
            if m in query_lower:
                if m == "focus":
                    mood = "chill" # Map focus to chill
                elif m == "sad":
                    mood = "somber"
                elif m == "upbeat":
                    mood = "happy"
                else:
                    mood = m
                logger.debug(f"  -> Found mood intent: {mood}")
                break

        # 3. Parse Energy
        if any(word in query_lower for word in ["high energy", "pumped", "workout", "intense", "fast"]):
            energy = 0.9
            logger.debug("  -> Found high energy intent")
        elif any(word in query_lower for word in ["low energy", "sleep", "tired", "calm", "slow"]):
            energy = 0.2
            logger.debug("  -> Found low energy intent")
        elif any(word in query_lower for word in ["focus", "study", "relax"]):
            energy = 0.4
            logger.debug("  -> Found medium-low energy intent")

        # 4. Parse acoustic
        if any(word in query_lower for word in ["acoustic", "unplugged", "guitar"]):
            likes_acoustic = True
            logger.debug("  -> Found acoustic intent")

        profile = UserProfile(
            favorite_genre=genre,
            favorite_mood=mood,
            target_energy=energy,
            likes_acoustic=likes_acoustic
        )
        logger.info(f"[Agent] Parsed Profile: {profile}")
        return profile

    def select_strategy(self, profile: UserProfile, query: str) -> str:
        """
        Selects the best scoring strategy based on the query and profile.
        """
        query_lower = query.lower()
        if "vibe" in query_lower or "mood" in query_lower or profile.favorite_mood in ["chill", "somber", "melancholic"]:
            strategy = "mood_first"
        elif "workout" in query_lower or "pumped" in query_lower or profile.target_energy > 0.8:
            strategy = "energy_focused"
        elif "only" in query_lower and profile.favorite_genre in query_lower:
            strategy = "genre_first"
        else:
            strategy = "balanced"
            
        logger.info(f"[Agent] Selected scoring strategy: {strategy}")
        return strategy

    def process_request(self, query: str, guardrails: List[Any] = None) -> Tuple[List[Dict[str, Any]], UserProfile, str]:
        """
        The main Plan -> Act -> Check loop.
        """
        logger.info("=== Agentic Workflow Started ===")
        # 1. Plan
        profile = self.parse_intent(query)
        strategy = self.select_strategy(profile, query)
        
        # 2. Act
        prefs = {
            "favorite_genre": profile.favorite_genre,
            "favorite_mood": profile.favorite_mood,
            "target_energy": profile.target_energy,
            "likes_acoustic": profile.likes_acoustic,
            "scoring_mode": strategy
        }
        
        logger.info("[Agent] Retrieving recommendations from catalog...")
        recommendations = recommend_songs(
            user_prefs=prefs,
            songs=self.catalog,
            k=10, # Retrieve more so we can filter
            scoring_mode=strategy,
            apply_diversity=True
        )
        
        # 3. Check (Guardrails)
        if guardrails:
            logger.info("[Agent] Applying Guardrails (Check phase)...")
            safe_recs = []
            for rec in recommendations:
                song, score, reasons = rec
                is_safe = True
                for guardrail in guardrails:
                    passed, reason = guardrail.evaluate(profile, song)
                    if not passed:
                        logger.warning(f"  [Guardrail Triggered] '{song['title']}' rejected: {reason}")
                        is_safe = False
                        break
                if is_safe:
                    safe_recs.append(rec)
            recommendations = safe_recs[:5] # Return top 5 safe
        else:
            recommendations = recommendations[:5]
            
        logger.info(f"=== Agentic Workflow Completed. Returned {len(recommendations)} songs. ===")
        return recommendations, profile, strategy
