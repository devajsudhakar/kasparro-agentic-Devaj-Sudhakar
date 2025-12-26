# Project Documentation

## 1. Problem Statement
The core challenge addressed by this project is **safely integrating Large Language Models (LLMs) into production-critical workflows** where accuracy is paramount. In domains like e-commerce and marketing, "creative" generation often leads to hallucinations, schema drift, and factually incorrect claims about products.

This system solves the problem of generating structured, high-quality content from raw data while strictly enforcing:
*   **Safety**: Preventing the invention of non-existent features or ingredients.
*   **Reliability**: Ensuring outputs always match strict JSON schemas, regardless of LLM variability.
*   **Engineering Rigor**: Prioritizing strict validation and "fail-loud" error handling over unconstrained text generation.

## 2. Why an Agentic Architecture
Instead of a single monolithic script or a "god prompt," this system utilizes a **multi-agent architecture** to separate concerns and maximize control.

*   **Decomposed Responsibilities**: Each agent handles a specific cognitive task. The `Parser Agent` normalizes data, the `Analysis Agent` identifies gaps, and the `Content Agent` focuses solely on generation. This makes the system easier to test, debug, and maintain.
*   **Targeted LLM Usage**: LLMs are used for semantic tasks (content generation, reasoning), while structural tasks (parsing, page assembly) remain deterministic code.
*   **Orchestration**: A central orchestrator (LangGraph) manages the state and data flow between agents, ensuring that no agent has access to data outside its scope.

## 3. Safety, Guardrails, and Strictness
This project implements a "Safety-First" approach to AI engineering, ensuring that the system is resilient enough for production deployment.

### Schema-Constrained Outputs
All LLM outputs are strictly validated against **Pydantic models** (`ContentSchema`, `QuestionOutputSchema`). If the LLM produces malformed JSON or violates the schema, the system catches the error immediately.

### Anti-Hallucination Guardrails
*   **Strict Prompting**: Prompts explicitly forbid the invention of facts (except for the specific case of inventing a fictional competitor for comparison purposes).
*   **Context Grounding**: The LLM is provided *only* with the parsed, normalized data, limiting its ability to pull in external, potentially incorrect knowledge.

### Fail-Loud Philosophy
Unlike previous iterations that used deterministic fallbacks, this version of the pipeline is designed to **fail loudly**.
*   **No Silent Failures**: If the LLM cannot produce valid data after 5 retries, the system raises a `RuntimeError` and crashes. This is a deliberate design choice to prevent bad data from silently propagating through the system.
*   **Aggressive Retries**: To balance strictness with the probabilistic nature of LLMs, agents attempt generation up to 5 times before giving up.

### Active Self-Correction & Validation
*   **Orchestrator Validation**: The LangGraph orchestrator includes a validation node that checks if the `Questions Agent` generated the required 15 Q&A pairs. If not, it routes the task back for a retry.

## 4. Solution Overview
The solution is a modular, multi-agent pipeline designed to process product data through distinct stages of normalization, analysis, and assembly.

*   **Parser Agent**: Normalizes raw input.
*   **Analysis Agent**: Identifies data gaps and generates observations using **ChatGroq**.
*   **Content Agent**: Generates core content blocks using **ChatGroq**.
*   **Evaluator Agent**: Validates content quality.
*   **Questions Agent**: Generates exactly 15 user-facing Q&A pairs using **ChatGroq**.
*   **Comparison Agent**: Performs side-by-side competitive analysis. Invents a fictional competitor if one is missing.
*   **Page Builder Agent**: Assembles final page templates.

## 5. System Design
The system architecture is defined by strict boundaries and explicit contracts between agents.

### Agent Boundaries & Contracts
*   **Orchestrator**: The central controller that manages data flow. It passes outputs from one agent as inputs to the next.
*   **Schema-Driven**: All inter-agent communication is validated against Pydantic models (defined in `schemas.py`).

### Orchestration Flow (LangGraph)
The pipeline executes as a state graph with conditional routing:
1.  **Parser Agent**: `Raw Dict` → `ParsedInputSchema`. Cleans and types data.
2.  **Analysis Agent**: `ParsedInputSchema` → `AnalysisSchema`.
3.  **Content Agent**: `ParsedInputSchema` + `AnalysisSchema` → `ContentSchema`.
4.  **Questions Agent**: `ParsedInputSchema` → `QuestionOutputSchema`. Generates categorized Q&A.
    *   *Validation*: Checks if 15 pairs exist. If not, retry (up to 3 times).
5.  **Comparison Agent**: `ParsedInputSchema` → `ComparisonSchema`. Determines winners for skin types.
6.  **Page Builder Agent**: Aggregates all outputs into `PageTemplates`.

## 6. Output Artifacts
The system produces machine-readable JSON artifacts in the `outputs/` directory:

*   **`analysis.json`**: Contains data health checks and observations.
*   **`content.json`**: The core marketing copy and structured attributes.
*   **`comparison.json`**: Side-by-side competitive analysis with verdicts.
*   **`pages.json`**: The final, ready-to-render page structures for the Product, FAQ, and Comparison views.
