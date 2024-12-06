import re
import requests
import openai
import json
import time
from .config import Config
import logging

openai.api_key = Config.OPENAI_API_KEY

# Set up logger
logger = logging.getLogger()

# Log application start
logger.info("Application started and logging configured.")

def get_embedding(text):
    """
    Fetches an embedding for the provided text using OLLAMA API.
    """
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
    """
    Classifies the provided query text by:
    - Generating an embedding for the query
    - Searching for all documents in Elasticsearch (no score)
    - Returning the matched document's categories for classification
    """
    start_time = time.time()
    logger.debug(f"Classifying text: {query}")
    
    # Generate embedding for the query
    embedding = get_embedding(query)
    if not embedding:
        logger.warning("Failed to generate query embedding")
        raise ValueError("Failed to generate query embedding")

    # Elasticsearch query to match all documents
    search_query = {
        "query": {
            "match_all": {}  # Match all documents
        },
        "size": 1000,  # Increase size to fetch more documents per query
        "sort": [
            {"Category": {"order": "asc"}} 
        ]
    }

    all_documents = []
    try:
        # Perform the initial search query
        response = es.search(index="categories_db", body=search_query)

        # Extract documents and categories without considering the score
        all_documents.extend(
            {
                "Category": hit["_source"].get("Category", "")
            }
            for hit in response["hits"]["hits"]
        )

        # If there are more documents, paginate through the results
        while len(response["hits"]["hits"]) > 0:
            search_query["search_after"] = response["hits"]["hits"][-1]["sort"]
            response = es.search(index="categories_db", body=search_query)

            # Add the next set of results
            all_documents.extend(
                {
                    "Category": hit["_source"].get("Category", "")
                }
                for hit in response["hits"]["hits"]
            )

    except Exception as e:
        logger.error(f"Error while searching Elasticsearch: {e}")
    
    # Log the total number of documents retrieved
    logger.info(f"Found {len(all_documents)} documents in Elasticsearch")

    # Use documents for classification
    elapsed_time = round(time.time() - start_time, 2)
    logger.debug("Proceeding to classify using all documents")

    # Now call classify with the correct number of arguments (query, all_documents)
    category = classify(query, all_documents)

    logger.info(f"Classification completed in {elapsed_time} seconds")
    return {"category": category}, elapsed_time


def classify(query, documents):
    """
    Uses OpenAI to classify the query based on available categories and documents,
    prioritizing the highest-scoring document.
    """
    # Extract unique categories
    existing_categories = list({doc["Category"] for doc in documents})

    # Log categories for debugging
    logger.debug(f"Available categories: {existing_categories}")


    # Construct the prompt
    prompt = f"""
        **Instructions:**
        1. Analyze the query.
        2. Focus on the keywords in the query and your categories.
        3. Select the Category that most semantically matches and best describes the query. If you can't classify, just say "Unknown"

        **Available Categories:**
        Categories: {json.dumps(existing_categories, ensure_ascii=False)}

        **User Query:**
        {query}

        **Example Evaluation:**
        - **User Query**: "I need information about technical support."
        - **Selected Category**: "Support"
        - **Justification**: "The user's intent is directly related to technical support, which falls under the 'Support' category."

        **Rule**
        - Always respond with **Category**: [Exact Category Name]

        **Results Report:**
        **Category**: [One of the existing categories]
    """


    try:
        # Call the OpenAI API
        model = Config.MODEL
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an advanced AI that classifies text into predefined categories. "
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        # Log response details
        usage_info = response.get("usage", {})
        logger.info(f"Response from OpenAI received for query: {query}")
        logger.info(f"Total tokens used: {usage_info.get('total_tokens', 'N/A')}")
        logger.info(f"Prompt tokens: {usage_info.get('prompt_tokens', 'N/A')}")
        logger.info(f"Completion tokens: {usage_info.get('completion_tokens', 'N/A')}")
        logger.debug(f"Response content: {response['choices'][0]['message']['content']}")

        # Parse the response
        category = parse_openai_response(response['choices'][0]['message']['content'])
        logger.info(f"Classification result: Category - {category}")

    except Exception as e:
        # Log the error and set default classification
        logger.error(f"Error in OpenAI classification: {e}")
        category = "Unknown"

    return category


def parse_openai_response(response_text):
    """
    Parses the OpenAI response text to extract the Category.
    """
    import re
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Log the full response text for debugging
        logger.debug(f"Full OpenAI response: {response_text}")
        
        # Regex to match the Category field (case-insensitive, flexible spacing)
        category_match = re.search(r"\*\*Category\*\*:?\s*(.+?)(?:\n|$)", response_text, re.IGNORECASE)
        
        # Extract the category if found
        if category_match:
            category = category_match.group(1).strip().strip('"')  # Remove surrounding quotes if any
            logger.info(f"Parsed Category: {category}")
        else:
            category = "Unknown"
            logger.warning("Category not found in response")
        
        return category
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return "Unknown"
