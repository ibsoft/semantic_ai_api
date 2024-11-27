import requests
import openai
import json
import time
from .config import Config
import logging

openai.api_key = Config.OPENAI_API_KEY

logger = logging.getLogger()

logger.info("Application started and logging configured with Redis.")

def get_embedding(text):
    headers = {"Content-Type": "application/json; charset=utf-8"}
    payload = {"model": Config.OLLAMA_MODEL, "prompt": text}
    try:
        response = requests.post(Config.OLLAMA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully fetched embedding for text: {text}")
        return response.json().get("embedding", None)
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def classify_text(query, es):
    start_time = time.time()
    logger.debug(f"Classifying text: {query}")
    embedding = get_embedding(query)
    if not embedding:
        logger.warning("Failed to generate query embedding")
        raise ValueError("Failed to generate query embedding")

    search_query = {
        "knn": {
            "field": "embedding",
            "query_vector": embedding,
            "k": 5,
            "num_candidates": 10
        }
    }

    try:
        response = es.search(index="documents", body={"query": search_query})
        documents = [
            {
                "Category": hit["_source"].get("Category", ""),
                "Sub-Category": hit["_source"].get("Sub-Category", ""),
                "Description": hit["_source"].get("Description", "")
            }
            for hit in response["hits"]["hits"]
        ]
        logger.debug(f"Found {len(documents)} documents for query")
    except Exception as e:
        logger.error(f"Error while searching Elasticsearch: {e}")
        documents = []

    elapsed_time = round(time.time() - start_time, 2)
    category, subcategory = classify(query, documents)
    logger.info(f"Classification completed in {elapsed_time} seconds")
    return {"category": category, "subcategory": subcategory}, elapsed_time

def classify(query, documents):
    context = [{"Category": doc["Category"], "Sub-Category": doc["Sub-Category"], "Description": doc["Description"]} for doc in documents]
    
    existing_categories = list({doc["Category"] for doc in documents})
    existing_subcategories = list({doc["Sub-Category"] for doc in documents})

    prompt = f"""
    Classify the user query into one of the existing categories and subcategories:
    Categories: {existing_categories}
    Subcategories: {existing_subcategories}
     
    Orders: Do not mix and match a category with other sub-categories but use as is.

    Use the context below as examples to help classify the query:
    {json.dumps(context, ensure_ascii=False)}

    User Query: {query}

    Respond with:
    **Category**: [One of the existing categories]
    **Sub-Category**: [One of the existing subcategories]
    """
    
    try:
        model = Config.MODEL
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "system", "content": "You are a strict classifier. Classify the query into one of the existing categories and subcategories."}, {"role": "user", "content": prompt}]
        )
        
        # Log the response details
        usage_info = response.get('usage', {})
        logger.info(f"Response from OpenAI received for query: {query}")
        logger.info(f"Total tokens used: {usage_info.get('total_tokens', 'N/A')}")
        logger.info(f"Prompt tokens: {usage_info.get('prompt_tokens', 'N/A')}")
        logger.info(f"Completion tokens: {usage_info.get('completion_tokens', 'N/A')}")
        logger.debug(f"Response content: {response['choices'][0]['message']['content']}")
        
        category, subcategory = parse_openai_response(response['choices'][0]['message']['content'])
        logger.info(f"Classification result: Category - {category}, Sub-Category - {subcategory}")
    except Exception as e:
        logger.error(f"Error in OpenAI classification: {e}")
        category, subcategory = "Unknown", "Unknown"

    return category, subcategory

def parse_openai_response(response_text):
    try:
        lines = response_text.split("\n")
        category = next((line.split(":")[1].strip() for line in lines if line.startswith("**Category**")), "Unknown")
        subcategory = next((line.split(":")[1].strip() for line in lines if line.startswith("**Sub-Category**")), "Unknown")
        return category, subcategory
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return "Unknown", "Unknown"
