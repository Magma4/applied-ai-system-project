# System Architecture Diagram (Mermaid)

Copy and paste the following code into the [Mermaid Live Editor](https://mermaid.live/), then export it as a PNG and save it as `system_architecture.png` in this directory to avoid account limits.

```mermaid
flowchart TD
    UserPrompt([User Natural Language Prompt]) --> Agent["CuratorAgent<br/>(Intent Parser)"]
    
    subgraph Agentic Workflow
        Agent --> |"1. Plan"| Profile["UserProfile<br/>(Genre, Mood, Energy)"]
        Agent --> |"Selects Strategy"| Strategy["Initial Strategy<br/>(e.g., balanced)"]
        
        Strategy --> RAG["2. RAG<br/>(Knowledge Retrieval)"]
        RAG --> |"Augmented Intent"| Act["3. Act<br/>(Initial Retrieval)"]
        
        Act --> Reflect{"3. Reflect<br/>(Self-Evaluation)"}
        
        Reflect --> |"Energy Gap > 0.25"| Refine["4. Refine<br/>(Switch Strategy)"]
        Refine --> Act
        
        Reflect --> |"Meets Criteria"| Check["5. Check<br/>(Guardrail Layer)"]
    end
    
    subgraph Reliability Layer
        Check --> Alignment["Energy Alignment Check"]
        Check --> Safety["Mood Safety Check"]
    end
    
    Alignment -- Pass --> Final["Top 5 Safe Songs"]
    Safety -- Pass --> Final
    
    Final --> CLI([CLI Output])
    
    subgraph Testing & Human Oversight
        CLI --> Human["Human Review<br/>(Explainability & Trust)"]
        Tests["Pytest Suite"] -.-> |"Validates Logic"| Agent
        Tests -.-> |"Validates Safety"| Check
    end
    
    Agent -.-> Log[(logs/agent_reasoning.log)]
    Check -.-> Log
```
