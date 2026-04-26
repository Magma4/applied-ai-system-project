import pytest
from src.guardrails import EnergyAlignmentGuardrail, MoodSafetyGuardrail
from src.recommender import UserProfile

def test_energy_guardrail():
    guardrail = EnergyAlignmentGuardrail(max_variance=0.4)
    profile = UserProfile("pop", "happy", 0.9, False)
    
    # Safe song
    safe_song = {"energy": 0.8}
    passed, _ = guardrail.evaluate(profile, safe_song)
    assert passed is True
    
    # Unsafe song
    unsafe_song = {"energy": 0.2}
    passed, reason = guardrail.evaluate(profile, unsafe_song)
    assert passed is False
    assert "Energy variance too high" in reason

def test_mood_safety_guardrail():
    guardrail = MoodSafetyGuardrail()
    
    # Relaxed seeker
    profile = UserProfile("lofi", "relaxed", 0.3, True)
    
    # Safe song
    safe_song = {"mood": "chill"}
    passed, _ = guardrail.evaluate(profile, safe_song)
    assert passed is True
    
    # Unsafe song (Intense)
    unsafe_song = {"mood": "intense"}
    passed, reason = guardrail.evaluate(profile, unsafe_song)
    assert passed is False
    assert "Contradictory mood detected" in reason
