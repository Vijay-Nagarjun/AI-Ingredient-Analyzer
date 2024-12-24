Packaged Food Ingredient Analysis Project
This document outlines the approach and methodology for the Packaged Food Ingredient Analysis Project. The goal is to classify food ingredients, analyze their nutritional profile, and calculate a health score for each product. The project will involve using an LLM (Large Language Model) for ingredient classification and analysis.
Ingredient Classification & Analysis
Ingredients will be classified into categories such as Natural, Additives, Preservatives, Artificial Colors, and Highly Processed. Each ingredient will also receive a score for its processing level, health impact, and nutrient density, all on a 1-5 scale.
The primary categories are as follows:
1. **Natural**: Whole or minimally processed ingredients like vegetables, fruits, grains, etc.
2. **Additives**: Ingredients added to improve texture, flavor, or preservation, including artificial flavorings or colors.
3. **Preservatives**: Chemicals added to extend shelf life.
4. **Artificial Colors**: Synthetic colors used in the product to enhance appearance.
5. **Highly Processed**: Ingredients that have been altered significantly from their original form (e.g., refined oils, sugars).

LLM Integration & Scoring Methodology
The Large Language Model (LLM) will be used to perform two main tasks:
1. **Ingredient Classification**: The LLM will classify ingredients into one of the predefined categories.
2. **Scoring**: Each ingredient will receive scores for processing level, health impact, and nutrient density, based on general knowledge and common formulations.
The scoring will be as follows:
1. **Processing Level** (1-5): Reflects how processed the ingredient is, with 1 being the least processed and 5 being the most.
2. **Health Impact** (1-5): A measure of how beneficial or harmful the ingredient is for health.
3. **Nutrient Density** (1-5): A score based on the nutrient content of the ingredient, considering essential vitamins, minerals, and fiber.
In the absence of explicit ingredient proportions, the LLM will infer approximate percentages based on ingredient order, which is typically in descending order of weight.
Example Ingredient Breakdown
For a given product, such as Lay's Potato Chips, the LLM will output the following information:
Example Input Ingredients: 'Potatoes, Vegetable Oil (Sunflower, Corn, or Canola), Salt, Spices'
The LLM will classify and score the ingredients, and estimate the proportions based on typical formulations of potato chips.
Example Output (JSON Format):
{
  "ingredients": [
    {
      "name": "Potatoes",
      "category": "Natural",
      "processing_score": 1,
      "health_impact_score": 1,
      "nutrient_density_score": 2,
      "percentage": 60
    },
    {
      "name": "Vegetable Oil (Sunflower, Corn, or Canola)",
      "category": "Highly Processed",
      "processing_score": 4,
      "health_impact_score": 3,
      "nutrient_density_score": 4,
      "percentage": 30
    },
    {
      "name": "Salt",
      "category": "Natural",
      "processing_score": 1,
      "health_impact_score": 3,
      "nutrient_density_score": 5,
      "percentage": 7
    },
    {
      "name": "Spices",
      "category": "Natural",
      "processing_score": 2,
      "health_impact_score": 1,
      "nutrient_density_score": 3,
      "percentage": 3
    }
  ],
  "artificial_colors": [
    {
      "name": "Tartrazine (Yellow 5)",
      "health_impact_score": 4,
      "processing_score": 5,
      "percentage": 0.5
    }
  ],
  "classification_summary": {
    "Natural": ["Potatoes", "Salt", "Spices"],
    "Highly Processed": ["Vegetable Oil"],
    "Additives": [],
    "Preservatives": [],
    "Artificial Colors": ["Tartrazine"],
    "Artificial": []
  },
  "ingredient_percentages": {
    "Potatoes": 60,
    "Vegetable Oil (Sunflower, Corn, or Canola)": 30,
    "Salt": 7,
    "Spices": 3,
    "Tartrazine": 0.5
  },
  "health_score": 2.5,
  "nutrient_breakdown": {
    "Fiber": "2g",
    "Vitamin C": "5%",
    "Iron": "3%"
  }
}
Final Rating Calculation and Backend Logic
The final product rating will be calculated in the backend by assigning weightages to the scores for each ingredient.
Backend Calculation Logic (Python Code):
def calculate_final_rating(ingredients):
    weights = {
        "processing": 0.5,
        "health_impact": 0.3,
        "nutrient_density": 0.2
    }
    total_scores = {"processing": 0, "health_impact": 0, "nutrient_density": 0}
    total_percentage = 0

    for ingredient in ingredients:
        total_scores["processing"] += ingredient["processing_score"] * ingredient["percentage"] / 100
        total_scores["health_impact"] += ingredient["health_impact_score"] * ingredient["percentage"] / 100
        total_scores["nutrient_density"] += ingredient["nutrient_density_score"] * ingredient["percentage"] / 100
        total_percentage += ingredient["percentage"]

    final_score = (
        total_scores["processing"] * weights["processing"] +
        total_scores["health_impact"] * weights["health_impact"] +
        total_scores["nutrient_density"] * weights["nutrient_density"]
    )
    return round(final_score, 2)
# Example Usage
ingredients = [
    {"name": "Potatoes", "processing_score": 1, "health_impact_score": 1, "nutrient_density_score": 2, "percentage": 60},
    {"name": "Vegetable Oil", "processing_score": 4, "health_impact_score": 3, "nutrient_density_score": 4, "percentage": 30},
    {"name": "Salt", "processing_score": 1, "health_impact_score": 3, "nutrient_density_score": 5, "percentage": 7},
    {"name": "Spices", "processing_score": 2, "health_impact_score": 1, "nutrient_density_score": 3, "percentage": 3}
]
print(calculate_final_rating(ingredients))  # Output: 2.3

