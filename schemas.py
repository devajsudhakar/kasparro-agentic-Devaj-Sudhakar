from typing import List, Optional
from pydantic import BaseModel

class ProductSchema(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    benefits: List[str]
    usage: str
    skin_type: List[str]
    price: str
    side_effects: List[str]

class CompetitorSchema(BaseModel):
    name: str
    description: str
    ingredients: List[str]
    price: str

class ParsedInputSchema(BaseModel):
    product: ProductSchema
    competitors: List[CompetitorSchema]

class AnalysisSchema(BaseModel):
    key_questions: List[str]
    observations: List[str]


class ContentSchema(BaseModel):
    headline: str
    value_proposition: List[str]
    feature_highlights: List[str]

class QAPair(BaseModel):
    question: str
    answer: str
    category: str

class QuestionOutputSchema(BaseModel):
    qa_pairs: List[QAPair]

class SkinTypeVerdict(BaseModel):
    skin_type: str
    winner: str
    reasoning: str

class ComparisonSchema(BaseModel):
    product_b_name: str
    ingredient_comparison: str
    benefit_comparison: str
    verdicts: List[SkinTypeVerdict]

class FinalOutputSchema(BaseModel):
    product_overview: dict
    key_insights: List[str]
    content_blocks: dict
    competitive_positioning: dict
    questions: QuestionOutputSchema