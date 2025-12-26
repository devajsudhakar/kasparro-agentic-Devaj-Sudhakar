from typing import Dict, Any, List
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from schemas import QuestionOutputSchema

def generate_questions(parsed_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generates categorized Q&A pairs using an LLM with strict validation and aggressive retries.
    Fails loudly if generation fails after 5 attempts.
    """
    # Initialize LLM
    llm = ChatGroq(temperature=0, model="llama-3.3-70b-versatile")
    
    # Setup Parser
    parser = PydanticOutputParser(pydantic_object=QuestionOutputSchema)
    
    # Setup Prompt
    prompt = PromptTemplate(
        template="""You are a Q&A generation assistant.
Your task is to generate exactly 15 Q&A pairs based on the provided product information.

Constraints:
1. Generate exactly 15 Q&A pairs.
2. You MUST generate the ANSWER based on the product data.
3. If no competitor exists in the data, invent a fictional Product B for comparison questions.
4. Each Q&A pair must have a 'category'. Use these categories: Informational, Usage, Safety, Purchase, Comparison.
5. Output must be a valid JSON object matching the requested schema.

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
            print(f"Generating questions (Attempt {attempt + 1}/{max_retries})...")
            result = chain.invoke({"product_data": json.dumps(parsed_input, indent=2)})
            # Result is a QuestionOutputSchema object
            return result.dict()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            last_exception = e
            continue

    # Fail loudly if all retries fail
    raise RuntimeError(f"Failed to generate questions after {max_retries} attempts. Last error: {last_exception}")

