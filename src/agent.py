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
        Enhanced Agentic Workflow: Plan -> Act -> Reflect -> Refine.
        """
        logger.info("=== Enhanced Agentic Workflow Started ===")
        
        # 1. PLAN
        profile = self.parse_intent(query)
        strategy = self.select_strategy(profile, query)
        
        # 2. ACT (Initial attempt)
        logger.info(f"[Agent] Attempt 1: Strategy '{strategy}'")
        recommendations = self._retrieve(profile, strategy)
        
        # 3. REFLECT (Self-Evaluation)
        logger.info("[Agent] Reflecting on results...")
        avg_energy = sum(r[0]["energy"] for r in recommendations) / len(recommendations) if recommendations else 0
        energy_gap = abs(avg_energy - profile.target_energy)
        
        needs_refinement = False
        if energy_gap > 0.25 and strategy != "energy_focused":
            logger.warning(f"  [Reflection] Results energy ({avg_energy:.2f}) is too far from target ({profile.target_energy:.2f}).")
            needs_refinement = True
            strategy = "energy_focused"
        elif len(set(r[0]["genre"] for r in recommendations)) < 2:
            logger.warning("  [Reflection] Results lack genre diversity.")
            needs_refinement = True
            # We don't change strategy here, but we've noted the need
            
        # 4. REFINE (If needed)
        if needs_refinement:
            logger.info(f"[Agent] Refinement triggered. Retrying with strategy: '{strategy}'")
            recommendations = self._retrieve(profile, strategy)
        
        # 5. CHECK (Guardrails)
        if guardrails:
            logger.info("[Agent] Final Guardrail Check...")
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
            recommendations = safe_recs[:5]
        else:
            recommendations = recommendations[:5]
            
        logger.info(f"=== Workflow Completed. Final Strategy: {strategy}. ===")
        return recommendations, profile, strategy

    def _retrieve(self, profile: UserProfile, strategy: str) -> List[Tuple[Dict[str, Any], float, List[str]]]:
        """Internal helper for retrieval."""
        prefs = {
            "favorite_genre": profile.favorite_genre,
            "favorite_mood": profile.favorite_mood,
            "target_energy": profile.target_energy,
            "likes_acoustic": profile.likes_acoustic,
            "scoring_mode": strategy
        }
        return recommend_songs(
            user_prefs=prefs,
            songs=self.catalog,
            k=10,
            scoring_mode=strategy,
            apply_diversity=True
        )
