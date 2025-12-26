from typing import Dict, Any, List
import json
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from schemas import AnalysisSchema

# NO TOOLS IMPORTED

def analyze_input(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes input using a direct LLM call.
    STRICTLY LLM-ONLY: Crashes if analysis fails.
    """
    # Initialize LLM
    llm = ChatGroq(temperature=0, model="llama-3.3-70b-versatile")
    
    # Define System Message
    system_message = """You are an expert product analyst.
Your goal is to analyze the provided product data, identify gaps, and synthesize insights.

CRITICAL INSTRUCTIONS:
1. Analyze the product data to identify missing fields (Price, Ingredients, etc.).
2. Generate 3-5 key questions a user might have.
3. Generate 3-5 analytical observations.
4. If competitors are missing, explicitly note this in observations.
5. Output valid JSON matching AnalysisSchema: { "key_questions": [...], "observations": [...] }
"""

    # Execute
    input_str = json.dumps(parsed_input, indent=2)
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=input_str)
    ]
    
    # Direct LLM invocation (Chain pattern)
    result = llm.invoke(messages)
    
    output_str = result.content
    
    # Clean up code blocks
    if "```json" in output_str:
        output_str = output_str.split("```json")[1].split("```")[0].strip()
    elif "```" in output_str:
        output_str = output_str.split("```")[1].split("```")[0].strip()
        
    parsed_output = json.loads(output_str)
    
    # Validate against schema
    return AnalysisSchema(**parsed_output).dict()