# WebResearchManager Design Document

## Overview
The WebResearchManager is an advanced research system designed to support AI sales agents by creating rich, narrative-focused insights about companies and their customers. The system combines web research with psychological analysis to generate natural language insights that help AI agents understand and effectively engage with customers.

## Core Philosophy
The system is built around the principle that AI sales agents work best with rich, contextual narratives rather than purely structured data. Each component focuses on creating insights that:
- Tell a coherent story about the customer and company
- Provide emotional and psychological context
- Explain the "why" behind observations
- Include real-world examples and scenarios
- Maintain natural language flow
- Enable empathetic understanding

## Architecture Overview

### High-Level Components
```
WebResearchManager
├── ResearchAgents
│   ├── CustomerPsychologyAgent
│   │   ├── Narrative: Customer psychological profile and decision patterns
│   │   ├── Context: Emotional drivers and trust-building insights
│   │   └── Scenarios: Example interactions and psychological triggers
│   │
│   ├── PainPointsAgent
│   │   ├── Narrative: Story of customer challenges and impacts
│   │   ├── Context: Emotional and practical effects of pain points
│   │   └── Scenarios: Real-world examples of customer struggles
│   │
│   ├── ValuePropositionAgent
│   │   ├── Narrative: Value story and customer journey
│   │   ├── Context: Why features matter emotionally and practically
│   │   └── Scenarios: Success stories and value realization examples
│   │
│   ├── CompetitiveAnalysisAgent
│   │   ├── Narrative: Market story from customer perspective
│   │   ├── Context: Competitive dynamics affecting decisions
│   │   └── Scenarios: Customer choice scenarios and triggers
│   │
│   └── [Other Specialized Agents]
│       └── Each with narrative, context, and scenario focus
│
├── PsychologicalTools
│   ├── EmotionalInsightGenerator
│   │   └── Creates rich emotional context for narratives
│   ├── BehavioralPatternAnalyzer
│   │   └── Develops behavioral scenarios and examples
│   └── DecisionJourneyMapper
│       └── Creates narrative flow of customer decisions
│
└── NarrativeIntegration
    ├── StoryWeaver
    │   └── Combines agent narratives into coherent story
    ├── ContextEnricher
    │   └── Adds psychological and emotional depth
    └── ScenarioBuilder
        └── Creates practical examples for AI understanding
```

## Research Agent Design

Each research agent is designed to create three types of narrative content:

### 1. Core Narrative
- Rich, flowing description of findings
- Natural language explanation of insights
- Story-driven presentation of information
- Clear cause-and-effect relationships

### 2. Contextual Understanding
- Emotional and psychological background
- Why things matter to customers
- Relationship between different factors
- Hidden motivations and drivers

### 3. Practical Scenarios
- Real-world examples
- Specific situations and responses
- Customer interaction scenarios
- Success and failure cases

## Output Format

Research findings are presented in a narrative-rich Markdown format:

```markdown
## [Research Area] Insights

### The Story
[Rich narrative describing the key findings and their significance]

### Understanding Why
[Detailed context about motivations, emotions, and psychological factors]

### Real-World Examples
[Specific scenarios and examples that illustrate the insights]

### Guidance for AI Sales Agents
[Natural language advice on how to use these insights in sales conversations]
```

## Implementation Philosophy

### 1. Natural Language Focus
- Prioritize narrative flow over structured data
- Use storytelling to convey complex insights
- Maintain conversational tone
- Include rich context and examples

### 2. AI-Friendly Output
- Design narratives that AI agents can easily understand
- Include explicit context and relationships
- Provide clear guidance for practical application
- Use consistent narrative patterns

### 3. Customer-Centric Approach
- Tell stories from customer perspective
- Include emotional and psychological context
- Provide real-world scenarios
- Focus on practical application

## Technology Stack
- Python 3.8+
- LangChain for agent orchestration
- Claude 3 Sonnet for narrative generation
- Markdown for output formatting
- Rich for CLI interface

## Key Features
- Narrative-focused research output
- Psychological context generation
- Real-world scenario creation
- AI-friendly insight presentation
- Integrated storytelling approach

## Success Metrics
- AI agent comprehension of insights
- Natural conversation quality
- Customer engagement effectiveness
- Sales conversion improvements
- Narrative coherence and usefulness

# SalesManager Design Document

## Overview
The SalesManager is an AI-driven conversational system that leverages psychological sales techniques and rich narrative insights to engage in natural, empathetic sales conversations. It uses LangGraph for state management and LLM-driven psychological analysis to create authentic, personalized interactions that resonate with customers' emotional and practical needs.

## Core Philosophy
The SalesManager operates on the principle that effective sales conversations require deep psychological understanding and emotional intelligence. The system:
- Uses psychological analysis to guide conversation strategy
- Adapts sales techniques based on emotional context
- Maintains authentic, personalized dialogue
- Learns from interaction patterns
- Integrates research insights naturally

## Architecture Overview

### High-Level Components
```
SalesAgent
├── ConversationGraph (LangGraph)
│   ├── States
│   │   ├── Understanding
│   │   │   └── Initial rapport & psychological baseline
│   │   ├── ValuePresentation
│   │   │   └── Emotionally resonant value delivery
│   │   ├── TrustBuilding
│   │   │   └── Psychological trust reinforcement
│   │   └── Guidance
│   │       └── Confidence-building next steps
│   │
│   └── StateManager
│       ├── Current state
│       ├── Conversation history
│       └── Strategy context from research
│
├── PsychologicalEngine (LLM-Driven)
│   ├── Analyzer
│   │   Input: message, history, state, strategy
│   │   Output: emotional state, trust level, triggers
│   │
│   ├── StrategySelector
│   │   Input: analysis, strategy narrative, history
│   │   Output: psychological approach + reasoning
│   │
│   └── ResponseCrafter
│       Input: strategy, context, research insights
│       Output: psychologically-tuned response
│
├── ConversationManager
│   ├── StateTransitioner (LLM)
│   │   Input: state, analysis, history
│   │   Output: next state + reasoning
│   │
│   ├── ContextManager
│   │   ├── Customer profile
│   │   ├── Emotional journey
│   │   ├── Psychological insights
│   │   └── Strategy effectiveness
│   │
│   └── ResponseOrchestrator
│       ├── Combines psychological strategy
│       ├── Maintains conversation coherence
│       └── Ensures strategy alignment
```

## Conversation Flow

### 1. Message Processing
- Receive customer message
- Analyze psychological and emotional state
- Select appropriate psychological strategy
- Determine conversation state transition
- Craft psychologically-aware response
- Update conversation context

### 2. Psychological Analysis
- Assess emotional state and trust levels
- Identify psychological triggers
- Evaluate strategy effectiveness
- Track emotional journey
- Monitor trust development

### 3. Strategy Selection
- Choose psychological techniques based on:
  - Current emotional state
  - Conversation history
  - Research insights
  - Strategy effectiveness
  - Conversation goals

### 4. Response Generation
- Incorporate selected psychological strategy
- Maintain natural conversation flow
- Ensure emotional coherence
- Apply appropriate framing
- Progress sales narrative

## State Management

### 1. Understanding State
- Build psychological baseline
- Establish emotional connection
- Gather customer context
- Identify key triggers

### 2. ValuePresentation State
- Present emotionally resonant value
- Connect with psychological needs
- Use identified triggers effectively
- Build confidence through narrative

### 3. TrustBuilding State
- Address psychological barriers
- Reinforce emotional connection
- Build authentic relationship
- Demonstrate deep understanding

### 4. Guidance State
- Guide with psychological awareness
- Maintain emotional safety
- Build confidence in next steps
- Ensure readiness signals

## Implementation Approach

### 1. LLM Integration
- Use LLMs for psychological analysis
- Dynamic strategy selection
- Natural response generation
- State transition decisions

### 2. Context Management
- Maintain psychological profile
- Track emotional journey
- Monitor strategy effectiveness
- Store conversation history

### 3. Response Orchestration
- Combine multiple inputs:
  - Psychological strategy
  - Conversation state
  - Research insights
  - Historical context

## Success Metrics
- Emotional resonance
- Trust development
- Psychological strategy effectiveness
- Conversation naturalness
- Sales progression
- Customer engagement
- Conversion rate

## Key Features
- LLM-driven psychological analysis
- Dynamic sales technique selection
- Emotional state tracking
- Natural conversation flow
- Strategic sales progression
- Contextual memory
- Learning from interactions