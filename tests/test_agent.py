import pytest
from src.agent import CuratorAgent
from src.recommender import UserProfile

@pytest.fixture
def agent():
    # Mock catalog not strictly needed for parsing tests
    return CuratorAgent(catalog=[])

def test_agent_parse_intent_high_energy_pop(agent):
    profile = agent.parse_intent("I'm feeling pumped and need a high energy pop workout track.")
    assert profile.favorite_genre == "pop"
    assert profile.target_energy == 0.9
    
def test_agent_parse_intent_chill_lofi(agent):
    profile = agent.parse_intent("I'm tired and want to focus, maybe some acoustic lofi.")
    assert profile.favorite_genre == "lofi"
    assert profile.favorite_mood == "chill"
    assert profile.target_energy == 0.2
    assert profile.likes_acoustic is True

def test_agent_strategy_selection(agent):
    profile = UserProfile("pop", "happy", 0.9, False)
    strategy = agent.select_strategy(profile, "I need a high energy pop workout track")
    assert strategy == "energy_focused"
    
    profile2 = UserProfile("lofi", "chill", 0.3, True)
    strategy2 = agent.select_strategy(profile2, "Just chill vibes")
    assert strategy2 == "mood_first"
