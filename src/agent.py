import re
import logging
from typing import Dict, Any, List, Tuple
from src.recommender import UserProfile, recommend_songs, get_strategy_weights
from src.knowledge import KnowledgeRetriever

logger = logging.getLogger(__name__)

class CuratorAgent:
    """
    Agent responsible for parsing natural language into user intents, 
    selecting scoring strategies, and refining recommendations.
    """
    
    def __init__(self, catalog: List[Dict[str, Any]]):
        self.catalog = catalog
        self.knowledge_base = KnowledgeRetriever()

    def parse_intent(self, query: str) -> Tuple[UserProfile, bool, bool]:
        """
        Parses a natural language query into a structured UserProfile.
        This uses rule-based parsing to act deterministically.
        Returns: (UserProfile, found_genre_boolean, strict_mood_boolean)
        """
        query_lower = query.lower()
        logger.info(f"[Agent] Parsing intent for query: '{query}'")
        
        # Default baseline
        genre = "pop"
        mood = "happy"
        energy = 0.5
        likes_acoustic = False
        strict_mood = "vibe" in query_lower or "only" in query_lower

        # 1. Parse Genre
        genres = ["pop", "rock", "lofi", "classical", "jazz", "hip hop", "electronic", "ambient", "metal", "synthwave"]
        found_genre = False
        for g in genres:
            if g in query_lower:
                genre = g
                found_genre = True
                logger.debug(f"  -> Found genre intent: {g}")
                break
                
        # 2. Parse Mood
        moods = ["happy", "chill", "intense", "somber", "melancholic", "relaxed", "focus", "sad", "upbeat", "calm", "dreamy"]
        found_mood = False
        for m in moods:
            if m in query_lower:
                found_mood = True
                if m == "focus":
                    mood = "chill"
                elif m == "sad":
                    mood = "somber"
                elif m == "upbeat":
                    mood = "happy"
                elif m in ["calm", "dreamy"]:
                    mood = "chill"
                else:
                    mood = m
                logger.debug(f"  -> Found mood intent: {mood}")
                break

        # 3. Parse Energy and fallback Moods
        if any(word in query_lower for word in ["high energy", "pumped", "workout", "intense", "fast"]):
            energy = 0.9
            if not found_mood: mood = "intense"
            logger.debug("  -> Found high energy intent")
        elif any(word in query_lower for word in ["low energy", "sleep", "tired", "calm", "slow"]):
            energy = 0.15
            if not found_mood: mood = "chill" # Better default for tired than "happy"
            if "classical" not in query_lower and not found_genre:
                genre = "ambient" # Better default for sleep
            logger.debug("  -> Found low energy intent")
        elif any(word in query_lower for word in ["focus", "study", "relax"]):
            energy = 0.4
            if not found_mood: mood = "relaxed"
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
        return profile, found_genre, strict_mood

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

    def process_request(self, query: str, guardrails: List[Any] = None) -> Tuple[List[Tuple[Dict[str, Any], float, List[str]]], UserProfile, str, str]:
        """
        Enhanced Agentic Workflow: Plan -> Act -> Reflect -> Refine.
        Now includes RAG (Retrieval-Augmented Generation) for expert insights.
        """
        logger.info("=== Enhanced Agentic Workflow Started ===")
        
        # 1. PLAN
        profile, found_genre, strict_mood = self.parse_intent(query)
        strategy = self.select_strategy(profile, query)
        
        # 2. RAG (Augmentation)
        # Retrieve expert insight based on the detected intent
        insight = self.knowledge_base.retrieve_insight(query, profile.favorite_genre, profile.favorite_mood)
        logger.info(f"[RAG] Retrieved Expert Insight: {insight[:50]}...")
        
        # 3. ACT (Initial attempt)
        logger.info(f"[Agent] Attempt 1: Strategy '{strategy}'")
        recommendations = self._retrieve(profile, strategy, found_genre)
        
        # 3. REFLECT (Self-Evaluation)
        logger.info("[Agent] Reflecting on results...")
        if not recommendations:
             logger.warning("[Agent] No results found in initial attempt. Broadening search.")
             recommendations = self._retrieve(profile, strategy, False) # Fallback to soft genre
             
        avg_energy = sum(r[0]["energy"] for r in recommendations) / len(recommendations) if recommendations else 0
        energy_gap = abs(avg_energy - profile.target_energy)
        
        needs_refinement = False
        if energy_gap > 0.25 and strategy != "energy_focused":
            logger.warning(f"  [Reflection] Results energy ({avg_energy:.2f}) is too far from target ({profile.target_energy:.2f}).")
            needs_refinement = True
            strategy = "energy_focused"
            
        # 4. REFINE (If needed)
        if needs_refinement:
            logger.info(f"[Agent] Refinement triggered. Retrying with strategy: '{strategy}'")
            recommendations = self._retrieve(profile, strategy, found_genre)
        
        # 5. CHECK (Guardrails)
        logger.info("[Agent] Final Guardrail Check...")
        safe_recs = []
        for rec in recommendations:
            song, score, reasons = rec
            is_safe = True
            
            # Application of Strict Mood Filter (Stretch Feature)
            if strict_mood:
                allowed = [profile.favorite_mood.lower(), "ambient", "chill", "relaxed"]
                if song["mood"].lower() not in allowed:
                    logger.warning(f"  [Strict Mood] '{song['title']}' rejected: '{song['mood']}' does not match vibe.")
                    is_safe = False
            
            if is_safe and guardrails:
                for guardrail in guardrails:
                    passed, reason = guardrail.evaluate(profile, song)
                    if not passed:
                        logger.warning(f"  [Guardrail Triggered] '{song['title']}' rejected: {reason}")
                        is_safe = False
                        break
            if is_safe:
                safe_recs.append(rec)
        
        recommendations = safe_recs[:5]
            
        logger.info(f"=== Workflow Completed. Final Strategy: {strategy}. ===")
        return recommendations, profile, strategy, insight

    def _retrieve(self, profile: UserProfile, strategy: str, hard_genre: bool = False) -> List[Tuple[Dict[str, Any], float, List[str]]]:
        """Internal helper for retrieval."""
        prefs = {
            "favorite_genre": profile.favorite_genre,
            "favorite_mood": profile.favorite_mood,
            "target_energy": profile.target_energy,
            "likes_acoustic": profile.likes_acoustic,
            "scoring_mode": strategy
        }
        songs = self.catalog
        if hard_genre:
            songs = [s for s in self.catalog if s["genre"].lower() == profile.favorite_genre.lower()]
            
        return recommend_songs(
            user_prefs=prefs,
            songs=songs,
            k=10,
            scoring_mode=strategy,
            apply_diversity=True
        )
