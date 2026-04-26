# System Architecture Diagram (Mermaid)

Copy and paste the following code into the [Mermaid Live Editor](https://mermaid.live/), then export it as a PNG and save it as `system_architecture.png` in this directory to avoid account limits.

```mermaid
flowchart TD
    User([User Prompt]) --> Agent[CuratorAgent\n(Intent Parser)]
    
    subgraph Agentic Workflow
        Agent --> |1. Plan| Profile[UserProfile\n(Genre, Mood, Energy)]
        Agent --> |Selects| Strategy[Scoring Strategy\n(e.g., energy_focused)]
        
        Profile --> |2. Act| Recommender[Recommender Engine]
        Strategy --> Recommender
        
        Recommender --> |Raw Recommendations| Guardrails[Guardrail Layer]
        
        Guardrails --> |3. Check| Alignment[Energy Alignment\nMax Variance 0.4]
        Guardrails --> |3. Check| Safety[Mood Safety\nNo Contradictions]
    end
    
    Alignment -- Pass --> Final[Top 5 Safe Songs]
    Safety -- Pass --> Final
    
    Alignment -- Fail --> Drop[Rejected/Filtered]
    Safety -- Fail --> Drop
    
    Final --> Out([Output to CLI/User])
    
    Agent -.-> Log[(logs/agent_reasoning.log)]
    Guardrails -.-> Log
```
