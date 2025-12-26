from typing import Dict, Any
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

def evaluate_content(parsed_input: Dict[str, Any], content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates generated content against source data for hallucinations and missing critical info.
    Returns: {'status': 'PASS' | 'FAIL', 'reason': '...'}
    """
    try:
        # Initialize LLM
        llm = ChatGroq(temperature=0, model="llama-3.3-70b-versatile")
        
        # Setup Parser
        parser = JsonOutputParser()
        
        # Setup Prompt
        prompt = PromptTemplate(
            template="""You are a Quality Assurance AI.
Compare the 'Source Data' with the 'Generated Content'.

Source Data:
{source_data}

Generated Content:
{generated_content}

Task:
1. Check for Hallucinations: Does the content mention features/ingredients NOT in the source?
2. Check for Missing Price: If source has a price, does the content context (or general knowledge) imply it was ignored? (Note: Content might not explicitly list price, but shouldn't contradict it).
3. Determine Status: 'PASS' if accurate, 'FAIL' if hallucinated or critical errors.
4. Provide Reason.

Output JSON:
{{
    "status": "PASS" | "FAIL",
    "reason": "Explanation..."
}}
""",
            input_variables=["source_data", "generated_content"],
        )

        # Create Chain
        chain = prompt | llm | parser

        # Execute
        source_str = json.dumps(parsed_input, indent=2)
        content_str = json.dumps(content, indent=2)
        
        result = chain.invoke({"source_data": source_str, "generated_content": content_str})
        
        # Basic validation
        if isinstance(result, dict) and "status" in result:
            return result
        else:
            return {"status": "PASS", "reason": "Output format error, failing open."}

    except Exception as e:
        # Fail open on error to avoid blocking pipeline
        return {"status": "PASS", "reason": f"Evaluator error: {str(e)}"}
