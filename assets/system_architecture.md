# System Architecture Diagram (Mermaid)

Copy and paste the following code into the [Mermaid Live Editor](https://mermaid.live/), then export it as a PNG and save it as `system_architecture.png` in this directory to avoid account limits.

```mermaid
flowchart TD
    UserPrompt([User Natural Language Prompt]) --> Agent[CuratorAgent\n(Intent Parser)]
    
    subgraph Agentic Workflow
        Agent --> |1. Plan| Profile[UserProfile\n(Genre, Mood, Energy)]
        Agent --> |Selects| Strategy[Scoring Strategy\n(e.g., energy_focused)]
        
        Profile --> |2. Act| Recommender[Recommender Engine\n(Retriever)]
        Strategy --> Recommender
        
        Recommender --> |Raw Recommendations| Guardrails[Guardrail Layer\n(Internal Evaluator)]
        
        Guardrails --> |3. Check| Alignment[Energy Alignment Check]
        Guardrails --> |3. Check| Safety[Mood Safety Check]
    end
    
    Alignment -- Pass --> Final[Top 5 Safe Songs]
    Safety -- Pass --> Final
    
    Final --> CLI([CLI Output])
    
    subgraph Testing & Human Oversight
        CLI --> Human[Human Review\n(Explainability & Trust)]
        Tests[Pytest Suite\n(test_agent, test_guardrails)] -.-> |Validates Logic| Agentic
        Tests -.-> |Validates Safety| Guardrails
    end
    
    Agent -.-> Log[(logs/agent_reasoning.log)]
    Guardrails -.-> Log
```
