# Agentic Content Pipeline: A Robust Multi-Agent System

## Abstract
This project represents a deep dive into **Agentic AI Engineering**, demonstrating how to build reliable, production-grade systems using Large Language Models (LLMs). Unlike simple API wrappers, this system employs a **multi-agent architecture** orchestrated by **LangGraph** to manage complex content generation tasks while enforcing strict safety guardrails. The system is powered by **Groq** (using Llama-3.3-70b) for high-speed, high-quality inference.

## 🏗️ Architectural Design
The system is designed around the **Single Responsibility Principle**, decomposing the content generation pipeline into specialized agents managed by a state graph. This modular approach improves testability and allows for targeted optimization of each component.

### The Agent Swarm
1.  **Parser Agent (Deterministic)**:
    *   *Role*: Data normalization and sanitization.
    *   *Logic*: Pure Python. Ensures input data conforms to strict schemas before it ever reaches an LLM.
2.  **Analysis Agent (Direct LLM)**:
    *   *Role*: Insight extraction & Gap filling.
    *   *Logic*: **ChatGroq**. Analyzes product data to identify missing fields and generate analytical observations.
3.  **Content Agent (Probabilistic)**:
    *   *Role*: Creative generation (Headlines, Value Props).
    *   *Logic*: **ChatGroq**. Uses prompt engineering to generate marketing copy with aggressive retries.
4.  **Evaluator Agent (Quality Control)**:
    *   *Role*: Hallucination detection.
    *   *Logic*: **ChatGroq**. Compares generated content against source data.
5.  **Questions Agent (Probabilistic)**:
    *   *Role*: User intent modeling.
    *   *Logic*: **ChatGroq**. Generates exactly 15 detailed Q&A pairs.
6.  **Comparison Agent (Analytic)**:
    *   *Role*: Competitive positioning.
    *   *Logic*: **ChatGroq**. Performs side-by-side analysis. If a competitor is missing, it **invents a fictional competitor** to ensure the comparison format is maintained.
7.  **Page Builder Agent (Deterministic)**:
    *   *Role*: Template assembly.
    *   *Logic*: Logic-less templating. Maps structured outputs to final presentation layers (JSON artifacts).

## 🛡️ Engineering Decisions & Trade-offs

### 1. Strict Validation & "Fail Loud"
A critical realization was that **LLMs cannot be trusted blindly**. To mitigate hallucination and schema drift:
*   **Strict Schemas**: All outputs are validated against **Pydantic** models.
*   **No Fallbacks**: Unlike previous iterations, this system **does not** degrade to deterministic fallbacks. If the LLM fails to produce valid data after retries, the pipeline **crashes intentionally**. This ensures that no sub-par or unverified data ever silently enters the production stream.

### 2. Aggressive Retries
To handle the probabilistic nature of LLMs, agents implement an **aggressive retry policy** (up to 5 attempts). This maximizes the chance of success without compromising on the strict schema requirements.

### 3. Orchestration with LangGraph
The pipeline uses **LangGraph** to manage state and control flow. This allows for complex behaviors like:
*   **Validation Loops**: The orchestrator checks if the Questions Agent generated the required 15 pairs. If not, it routes the task back for a retry.
*   **Conditional Routing**: The graph ensures data flows logically from parsing to analysis to generation.

## 🛠️ Technology Stack
*   **Language**: Python 3.10+
*   **Orchestration**: LangGraph (StateGraph, Conditional Edges)
*   **LLM Provider**: Groq (Llama-3.3-70b-versatile)
*   **Framework**: LangChain (ChatGroq, PydanticOutputParser)
*   **Validation**: Pydantic (for strict type enforcement)

## 🚀 How to Run
This project is designed to be "clone-and-run" ready.

1.  **Environment Setup**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
    pip install -r requirements.txt
    ```

2.  **Configuration**:
    Set your Groq API key in a `.env` file:
    ```env
    GROQ_API_KEY=gsk_...
    ```

3.  **Execution**:
    ```bash
    python run_pipeline.py
    ```
    *Check `outputs/` directory for the generated JSON artifacts.*

## 🎓 Learning Outcomes
Building this system reinforced the importance of **control flow** in AI systems. Moving from a linear script to a **graph-based architecture** (LangGraph) allowed me to implement complex behaviors like loops and conditional branching. The shift to **strict validation** and **Groq** demonstrates how to build high-performance, reliable AI applications that prioritize correctness over fault tolerance.
