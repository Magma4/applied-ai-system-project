# 🎵 Agentic VibeFinder: A Trustworthy Music Curator

### Project Context (Origin)
This project is an evolution of the **Music Recommender Simulation** developed in earlier modules. The original system was a standalone Python script designed to score a fixed CSV catalog using linear weights for genre, mood, and energy. It demonstrated the basics of content-based filtering but lacked a natural interface and safety checks.

---

## 🎯 Project Summary
**Agentic VibeFinder** transforms the original recommender into an end-to-end AI system. It introduces an **Agentic Workflow** that allows users to interact using natural language and implements **Reliability Guardrails** to ensure all recommendations align with the user's emotional intent. This project matters because it demonstrates how to build "Explainable AI" that prioritizes user trust over raw algorithmic matching.

## 🏗️ Architecture Overview
The system follows a **Plan -> Act -> Check** agentic loop:
1.  **Plan (CuratorAgent):** Parses fuzzy natural language (e.g., "I need to focus") into a structured user profile.
2.  **Act (Recommender Engine):** Retrieves the top candidates from the song catalog using a dynamically selected scoring strategy.
3.  **Check (Guardrail Layer):** Audits every candidate against "Safety" rules (Energy Alignment and Mood Consistency) to filter out jarring or contradictory results.

> [!NOTE]
> For a visual breakdown, see the [System Architecture Diagram](assets/system_architecture.md).

---

## 🚀 Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd applied-ai-system-project
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    python -m src.main
    ```

4.  **Run the tests:**
    ```bash
    PYTHONPATH=. pytest
    ```

---

## 🧪 Sample Interactions

### Example 1: High-Energy Intent
*   **Input:** *"I'm feeling pumped and need a high energy pop workout track."*
*   **Agent Reasoning:** Parsed as `Genre: pop`, `Mood: happy`, `Energy: 0.9`. Selected `energy_focused` strategy.
*   **Output:** Recommends tracks like **"Storm Runner"** (Score 4.66) with clear reasoning: `genre match`, `mood match`, and a high `energy fit`.

### Example 2: Focus & Calm Intent
*   **Input:** *"I'm tired and want to focus, maybe some acoustic lofi."*
*   **Agent Reasoning:** Parsed as `Genre: lofi`, `Mood: chill`, `Energy: 0.2`, `Acoustic: True`. Selected `mood_first` strategy.
*   **Output:** Recommends **"Midnight Rain"** and **"Coffee Shop Stories"**, prioritizing the `mood match` and `acoustic` bonus while keeping energy low.

### Example 3: Adversarial/Conflict Handling
*   **Input:** *"I am very relaxed but I want intense rock."*
*   **Guardrail Action:** The Agent identified the contradiction. The **EnergyAlignmentGuardrail** triggered, rejecting songs like *"Dust Road Anthem"* because their energy levels were too high for a "relaxed" seeker, ensuring the final output remained safe.

---

## 🧠 Design Decisions & Trade-offs
*   **Deterministic vs. LLM Agent:** I chose to build a rule-based deterministic agent rather than using a live LLM API. 
    *   *Rationale:* This ensures the project is 100% reproducible and runs without external API keys. 
    *   *Trade-off:* The natural language vocabulary is more limited, but the "Decision Making" is 100% transparent and auditable.
*   **Multi-Stage Filtering:** I implemented the guardrails as a post-processing step.
    *   *Rationale:* This separates "Curation" (scoring) from "Safety" (guardrails), allowing us to log exactly *why* a song was rejected.

## 📈 Testing Summary
I implemented a `pytest` suite covering the Agent's intent parser and the individual Guardrail rules. 
*   **What worked:** The Energy Variance guardrail is highly effective at catching "vibe-clashing" songs.
*   **What I learned:** I learned that "Explainable AI" isn't just about the code; it's about the logs. Adding a dedicated reasoning log (`logs/agent_reasoning.log`) was the most helpful tool for debugging agent "hallucinations" in intent parsing.

## 💡 Reflection
This project taught me that the most powerful part of an AI system isn't the model itself, but the **workflow** surrounding it. Building the "Check" phase of the Agentic loop showed me how developers can wrap unpredictable AI outputs in "Safety Envelopes" (Guardrails) to create systems that users can actually trust in production.

---

## 🌟 Stretch Features (Extra Credits)
I implemented two advanced features to demonstrate system maturity:
1.  **Enhanced Agentic Workflow (+2):** The `CuratorAgent` now performs a **Plan -> Act -> Reflect -> Refine** loop. It evaluates its initial results (Reflection) and, if they don't meet the intent (e.g., energy gap too wide), it automatically refines its strategy and retries the search.
2.  **Evaluation Harness (+2):** I built a dedicated `src/eval_harness.py` script. It runs a **Golden Dataset** of adversarial prompts and prints a "System Evaluation Report" with PASS/FAIL status and confidence ratings, allowing for objective performance tracking.

---
*Created for the Applied AI System Project portfolio.*
