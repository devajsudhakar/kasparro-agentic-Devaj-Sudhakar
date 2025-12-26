from typing import Dict, Any
from schemas import ParsedInputSchema, ProductSchema, CompetitorSchema

def parse_input(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses raw input data into a structure strictly matching ParsedInputSchema.
    Does NOT infer or clean data excessively. Relies on Pydantic to validate presence of fields.
    """
    product_data = raw_input.get("product", {})
    competitors_data = raw_input.get("competitors", [])

    # Strictly map keys. If keys are missing, Pydantic will raise ValidationError.
    # We assume the input keys match the schema field names.
    
    product = ProductSchema(**product_data)
    
    competitors = [
        CompetitorSchema(**comp) for comp in competitors_data
    ]

    parsed = ParsedInputSchema(
        product=product,
        competitors=competitors
    )

    return parsed.dict()
