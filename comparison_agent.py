from typing import Dict, Any
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import ComparisonSchema

# DELETED: _generate_deterministic_comparison (This removes the bug and the audit violation)

def generate_comparison(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates a side-by-side comparison using an LLM.
    STRICTLY LLM-ONLY: Crashes if generation fails.
    """
    # Initialize LLM
    llm = ChatGroq(temperature=0, model="llama-3.3-70b-versatile")
    
    # Setup Parser
    parser = PydanticOutputParser(pydantic_object=ComparisonSchema)
    
    # Setup Prompt
    prompt = PromptTemplate(
        template="""You are a competitive analysis expert.
Compare 'Product A' (our product) with 'Product B' (competitor).

Product A:
{product_data}

Product B:
{competitor_data}

Task:
1. Compare ingredients and benefits.
2. Declare a winner for: Oily, Dry, Sensitive skin.
3. Provide reasoning for each verdict.
4. If Product B is missing, YOU MUST INVENT A FICTIONAL COMPETITOR named 'Product B' (e.g., 'Generic Vitamin C Serum') and populate the 'product_b_name' field.
5. Output strictly as JSON.

{format_instructions}
""",
        input_variables=["product_data", "competitor_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Prepare Data
    product_data = json.dumps(parsed_input.get("product", {}), indent=2)
    competitors = parsed_input.get("competitors", [])
    # Provide an empty dict if no competitor, prompting the LLM to invent one
    competitor_data = json.dumps(competitors[0] if competitors else {}, indent=2)

    # Create Chain
    chain = prompt | llm | parser

    # Execute with retries but NO fallback return
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = chain.invoke({"product_data": product_data, "competitor_data": competitor_data})
            return result.dict()
        except Exception as e:
            if attempt == max_retries - 1:
                # Fail loudly!
                raise RuntimeError(f"Comparison generation failed after {max_retries} attempts: {e}")
            continue