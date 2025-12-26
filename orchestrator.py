from typing import Dict, Any, TypedDict, List, Literal
import json
from pathlib import Path
from langgraph.graph import StateGraph, END

from parser_agent import parse_input
from analysis_agent import analyze_input
from content_agent import generate_content
from question_agent import generate_questions
from comparison_agent import generate_comparison
from page_builder_agent import build_pages
from evaluator_agent import evaluate_content

# Define the Graph State
class GraphState(TypedDict):
    raw_input: Dict[str, Any]
    parsed_input: Dict[str, Any]
    analysis: Dict[str, Any]
    content: Dict[str, Any]
    questions: Dict[str, Any] # Changed to Any to accommodate QuestionOutputSchema dict
    comparison: Dict[str, Any]
    pages: Dict[str, Any]
    qa_retries: int # Track Q&A retries
    evaluation_status: str

# Define Nodes
def parser_node(state: GraphState) -> Dict[str, Any]:
    print("--- PARSER AGENT ---")
    parsed = parse_input(state["raw_input"])
    return {"parsed_input": parsed}

def analysis_node(state: GraphState) -> Dict[str, Any]:
    print("--- ANALYSIS AGENT ---")
    analysis = analyze_input(state["parsed_input"])
    return {"analysis": analysis}

def content_node(state: GraphState) -> Dict[str, Any]:
    print("--- CONTENT AGENT ---")
    content = generate_content(state["parsed_input"], state["analysis"])
    return {"content": content}

def questions_node(state: GraphState) -> Dict[str, Any]:
    print(f"--- QUESTIONS AGENT (Attempt {state.get('qa_retries', 0) + 1}) ---")
    questions = generate_questions(state["parsed_input"])
    return {"questions": questions, "qa_retries": state.get("qa_retries", 0) + 1}

def validation_node(state: GraphState) -> Dict[str, Any]:
    print("--- VALIDATION NODE ---")
    # Check if we have 15 questions
    qa_pairs = state["questions"].get("qa_pairs", [])
    count = len(qa_pairs)
    print(f"Generated {count} Q&A pairs.")
    return {} # Just a pass-through node for logic, state update handled in conditional edge or here if needed

def comparison_node(state: GraphState) -> Dict[str, Any]:
    print("--- COMPARISON AGENT ---")
    comparison = generate_comparison(state["parsed_input"])
    return {"comparison": comparison}

def page_builder_node(state: GraphState) -> Dict[str, Any]:
    print("--- PAGE BUILDER AGENT ---")
    pages = build_pages(state["parsed_input"], state["content"], state["questions"])
    return {"pages": pages}

# Conditional Logic
def check_qa_count(state: GraphState) -> Literal["retry", "next"]:
    qa_pairs = state["questions"].get("qa_pairs", [])
    count = len(qa_pairs)
    retries = state.get("qa_retries", 0)
    
    if count < 15:
        if retries >= 3:
            raise RuntimeError(f"Failed to generate 15 questions after {retries} attempts. Got {count}.")
        print(f">>> Insufficient questions ({count}/15). Retrying...")
        return "retry"
    
    return "next"

# Build the Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("parser", parser_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("content", content_node)
workflow.add_node("questions", questions_node)
workflow.add_node("validation", validation_node)
workflow.add_node("comparison", comparison_node)
workflow.add_node("page_builder", page_builder_node)

# Add Edges
workflow.set_entry_point("parser")
workflow.add_edge("parser", "analysis")
workflow.add_edge("analysis", "content")
workflow.add_edge("content", "questions")
workflow.add_edge("questions", "validation")

# Conditional Edge for Validation
workflow.add_conditional_edges(
    "validation",
    check_qa_count,
    {
        "retry": "questions",
        "next": "comparison"
    }
)

workflow.add_edge("comparison", "page_builder")
workflow.add_edge("page_builder", END)

# Compile the Graph
app = workflow.compile()

def run_pipeline(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs the full multi-agent pipeline using LangGraph.
    """
    # Initialize state
    initial_state = {"raw_input": raw_input, "qa_retries": 0, "evaluation_status": "PASS"}
    
    # Run the graph
    # No global try-except here. If it fails, it crashes.
    final_state = app.invoke(initial_state)
    
    return final_state

def save_outputs(outputs: Dict[str, Any], output_dir: str = "outputs") -> None:
    """
    Saves pipeline outputs as JSON files.
    """
    Path(output_dir).mkdir(exist_ok=True)

    with open(f"{output_dir}/analysis.json", "w") as f:
        json.dump(outputs.get("analysis", {}), f, indent=2)

    with open(f"{output_dir}/content.json", "w") as f:
        json.dump(outputs.get("content", {}), f, indent=2)
        
    with open(f"{output_dir}/comparison.json", "w") as f:
        json.dump(outputs.get("comparison", {}), f, indent=2)

    with open(f"{output_dir}/pages.json", "w") as f:
        json.dump(outputs.get("pages", {}), f, indent=2)
