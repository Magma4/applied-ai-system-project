from typing import Dict, Any, Tuple
from abc import ABC, abstractmethod
from src.recommender import UserProfile

class Guardrail(ABC):
    """Base class for reliability guardrails."""
    
    @abstractmethod
    def evaluate(self, profile: UserProfile, song: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluate if a song is safe to recommend for the given profile.
        Returns: (is_safe, failure_reason)
        """
        pass

class EnergyAlignmentGuardrail(Guardrail):
    """Ensures the recommended song doesn't exceed a specific variance from target energy."""
    
    def __init__(self, max_variance: float = 0.4):
        self.max_variance = max_variance

    def evaluate(self, profile: UserProfile, song: Dict[str, Any]) -> Tuple[bool, str]:
        song_energy = float(song["energy"])
        target_energy = profile.target_energy
        variance = abs(song_energy - target_energy)
        
        if variance > self.max_variance:
            return False, f"Energy variance too high: {variance:.2f} > {self.max_variance:.2f} (Song: {song_energy}, Target: {target_energy})"
        return True, ""

class MoodSafetyGuardrail(Guardrail):
    """Prevents highly contradictory moods (e.g., Intense song for Relaxed seeker)."""
    
    def __init__(self):
        self.unsafe_pairs = {
            "chill": ["intense", "euphoric", "angry"],
            "relaxed": ["intense", "euphoric", "angry"],
            "somber": ["happy", "euphoric", "upbeat"],
            "happy": ["somber", "melancholic", "angry"]
        }

    def evaluate(self, profile: UserProfile, song: Dict[str, Any]) -> Tuple[bool, str]:
        target_mood = profile.favorite_mood.lower()
        song_mood = song["mood"].lower()
        
        if target_mood in self.unsafe_pairs:
            if song_mood in self.unsafe_pairs[target_mood]:
                return False, f"Contradictory mood detected: Song is '{song_mood}', Target is '{target_mood}'"
                
        return True, ""
