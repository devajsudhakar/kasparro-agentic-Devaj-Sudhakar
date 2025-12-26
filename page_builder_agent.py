from typing import Dict, Any, List


def build_pages(
    parsed_input: Dict[str, Any],
    content: Dict[str, Any],
    questions: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assembles final page-level templates from existing outputs.
    Returns a dictionary containing product_page, faq_page, and comparison_page.
    """
    product = parsed_input.get("product", {})
    competitors = parsed_input.get("competitors", [])

    # 1. Product Page
    product_page = {
        "headline": content.get("headline", ""),
        "description": product.get("description", ""),
        "benefits": product.get("benefits", []),
        "usage": product.get("usage", ""),
        "skin_type": product.get("skin_type", []),
        "price": product.get("price", "")
    }

    # 2. FAQ Page
    faqs: List[Dict[str, str]] = []
    # Flatten all question categories
    for category_questions in questions.values():
        if isinstance(category_questions, list):
            for item in category_questions:
                if isinstance(item, dict):
                    faqs.append({
                        "question": item.get("question", ""),
                        "answer": item.get("answer", "Not provided.")
                    })
                elif isinstance(item, str): # Fallback for old format if needed
                     faqs.append({
                        "question": item,
                        "answer": "Not provided in input."
                    })


    faq_page = {
        "faqs": faqs
    }

    # 3. Comparison Page
    competitors_list: List[Dict[str, Any]] = []
    for comp in competitors:
        competitors_list.append({
            "name": comp.get("name", ""),
            "price": comp.get("price", ""),
            "ingredients": comp.get("ingredients", [])
        })

    comparison_page = {
        "product": product.get("name", ""),
        "competitors": competitors_list
    }

    return {
        "product_page": product_page,
        "faq_page": faq_page,
        "comparison_page": comparison_page
    }
