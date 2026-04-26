# Model Card — Music Recommender Simulation (Agentic Revamp)

## Model Name

**VibeFinder 2.0 (Agentic Curator)** — a transparent song ranker featuring natural language intent parsing and reliability guardrails.

---

## Goal / Task

The system takes **natural language prompts** (e.g., "I need a high energy pop workout track"), converts them into structured user profiles using an **Agentic Workflow**, retrieves matching songs, and finally applies **Reliability Guardrails** to filter out inappropriate recommendations. It prioritizes trustworthiness and explainability.

---

## Data Used

There are **18 songs** in `data/songs.csv`. Each row has genre, mood, energy, tempo, and advanced metadata like popularity and release decade. The set is tiny and made up; results are not population-level but serve to demonstrate AI reasoning loops.

---

## Architecture Summary

1. **Agentic Layer (`src/agent.py`)**:
   - **Intent Parsing**: Converts fuzzy natural language into discrete parameters (Genre, Mood, Energy).
   - **Strategy Selection**: Dynamically chooses the scoring mode (e.g., `energy_focused` vs `mood_first`) based on the query semantics.
2. **Recommender Core (`src/recommender.py`)**:
   - Scores songs based on a transparent, multi-factor rule system (adding points for matches).
3. **Guardrail Layer (`src/guardrails.py`)**:
   - **Energy Alignment**: Rejects songs if their energy variance from the target is > 0.4.
   - **Mood Safety**: Prevents contradictory recommendations (e.g., stopping an "Intense" track from reaching a "Relaxed" seeker).

---

## Observed Behavior / Biases

**Strict Filtering:** The new Guardrails successfully prevent the "Gym Hero" problem observed in V1.0. If a user asks for "Relaxed", intense pop tracks are blocked entirely.
**Deterministic Agent:** The Agent uses rule-based parsing rather than an LLM. While this limits its vocabulary (e.g., it only knows specific genre keywords), it guarantees **100% reproducibility** and eliminates hallucination.

---

## Evaluation Process

The system is evaluated using an integrated test suite (`tests/test_agent.py` and `tests/test_guardrails.py`) that checks:
- Proper mapping of natural language to `UserProfile`.
- Correct rejection of misaligned songs by the Guardrails.
- End-to-end execution of adversarial prompts (e.g., "Adversarial: I am very relaxed but I want intense rock").

---

## Intended Use and Non-Intended Use

**Intended:** **Teaching and demos.** Demonstrating how an "Agentic Loop" (Plan -> Act -> Check) can improve the reliability of a retrieval system.
**Not intended:** Production systems. A real production system would replace the deterministic agent with a fine-tuned LLM and use a vector database for retrieval.

---

## Personal Reflection

**Phase 2 Learnings:** Moving from a simple logic script to an "Agentic Workflow" showed how much value lies in the "Check" phase. The `Guardrails` are essentially "Quality Control" for AI. Even if the retrieval (scoring) makes a mistake, the guardrail catches it.
**Transparency:** Logging the Agent's decision-making process (`logs/agent_reasoning.log`) makes debugging significantly easier and builds trust in *why* a song was chosen or rejected.
