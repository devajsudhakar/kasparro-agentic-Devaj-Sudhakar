from typing import Dict, Any, List
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import ContentSchema
import json

def generate_content(parsed_input: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates structured content blocks using an LLM with strict validation and aggressive retries.
    Fails loudly if generation fails after 5 attempts.
    """
    # Initialize LLM
    llm = ChatGroq(temperature=0, model="llama-3.3-70b-versatile")
    
    # Setup Parser
    parser = PydanticOutputParser(pydantic_object=ContentSchema)
    
    # Setup Prompt
    prompt = PromptTemplate(
        template="""You are a content generation assistant.
Your task is to generate marketing content based STRICTLY on the provided product information.

Constraints:
1. Use ONLY the information provided in the 'Product Data'. Do NOT invent facts or hallucinate.
2. If specific information is missing, leave the corresponding field empty.
3. Output must be a valid JSON object matching the requested schema.

Product Data:
{product_data}

{format_instructions}
""",
        input_variables=["product_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Create Chain
    chain = prompt | llm | parser

    # Execute with 5 retries
    max_retries = 5
    last_exception = None

    for attempt in range(max_retries):
        try:
            print(f"Generating content (Attempt {attempt + 1}/{max_retries})...")
            result = chain.invoke({"product_data": json.dumps(parsed_input, indent=2)})
            return result.dict()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            last_exception = e
            continue

    # Fail loudly if all retries fail
    raise RuntimeError(f"Failed to generate content after {max_retries} attempts. Last error: {last_exception}")

