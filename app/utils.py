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
    - Searching for similar documents in Elasticsearch
    - Checking for a match by Title and Description
    - Returning the matched document's categories if found
    - Otherwise, classifying the query using the top results
    """
    start_time = time.time()
    logger.debug(f"Classifying text: {query}")
    
    # Generate embedding for the query
    embedding = get_embedding(query)
    if not embedding:
        logger.warning("Failed to generate query embedding")
        raise ValueError("Failed to generate query embedding")

    # Elasticsearch vector search query
    search_query = {
        "size": 5,  # Limit the results to the top 5 documents
        "query": {
            "knn": {
                "field": "embedding",  # The embedding field
                "query_vector": embedding,  # The query vector to match against stored embeddings
                "k": 5,  # Number of nearest neighbors to return
                "num_candidates": 10  # Number of candidates to consider for each match
            }
        }
    }

    try:
        # Perform the search query
        response = es.search(index="categories_index", body=search_query)

        # Initialize variables to track the highest-scoring document
        highest_score = -1  # Start with an impossible low score
        highest_score_doc = None

        # Iterate through results to check for exact or near match by Title and Description
        for hit in response["hits"]["hits"]:
            document = hit["_source"]
            score = hit["_score"]  # Get the Elasticsearch relevance score
            
            # Update the highest-scoring document if applicable
            if score > highest_score:
                highest_score = score
                highest_score_doc = document

            # Check for an exact match by Title or Description
            if (
                document.get("Title", "").strip().lower() == query.strip().lower() or
                document.get("Description", "").strip().lower() == query.strip().lower()
            ):
                logger.info(f"Exact match found for Title/Description: {document}")
                return {
                    "category": document.get("Category"),
                    "subcategory": document.get("Sub-Category"),
                    "subsubcategory": document.get("Sub-sub-Category")
                }, round(time.time() - start_time, 2)

        # Log the highest-scoring document if no exact match is found
        if highest_score_doc:
            title = highest_score_doc.get("Title", "No Title Available")
            logger.info(f"Highest scoring document title: {title} with score {highest_score}")

    except Exception as e:
        logger.error(f"Error while searching Elasticsearch: {e}")

    # If no exact match, proceed with regular classification
    elapsed_time = round(time.time() - start_time, 2)
    logger.debug("No exact match found, proceeding to classify using top documents")

    # Use top documents for classification
    documents = [
        {
            "Category": hit["_source"].get("Category", ""),
            "Sub-Category": hit["_source"].get("Sub-Category", ""),
            "Sub-sub-Category": hit["_source"].get("Sub-sub-Category", ""),
            "Description": hit["_source"].get("Description", ""),
            "Title": hit["_source"].get("Title", ""),
        }
        for hit in response["hits"]["hits"]
    ]
    category, subcategory, subsubcategory = classify(query, documents, highest_score_doc)
    
    logger.info(f"Classification completed in {elapsed_time} seconds")
    return {"category": category, "subcategory": subcategory, "subsubcategory": subsubcategory}, elapsed_time


def classify(query, documents, highest_score_doc):
    """
    Uses OpenAI to classify the query based on available categories and documents,
    prioritizing the highest-scoring document.
    """
    # Extract unique categories, subcategories, and sub-subcategories
    existing_categories = list({doc["Category"] for doc in documents})
    existing_subcategories = list({doc["Sub-Category"] for doc in documents})
    existing_sub_subcategories = list({doc["Sub-sub-Category"] for doc in documents})

    # Log categories for debugging
    logger.debug(f"Available categories: {existing_categories}")
    logger.debug(f"Available subcategories: {existing_subcategories}")
    logger.debug(f"Available sub-subcategories: {existing_sub_subcategories}")

    # Log the highest-scoring document details
    logger.info(f"Highest scoring document: {highest_score_doc.get('Title', 'N/A')} with score {highest_score_doc.get('Score', 'N/A')}")

    # Construct the highest-scoring document information
    highest_doc_info = f"""
    Title: {highest_score_doc.get('Title', 'N/A')}
    Description: {highest_score_doc.get('Description', 'N/A')}
    Category: {highest_score_doc.get('Category', 'N/A')}
    Sub-Category: {highest_score_doc.get('Sub-Category', 'N/A')}
    Sub-sub-Category: {highest_score_doc.get('Sub-sub-Category', 'N/A')}
    """

    

    # Construct the prompt
    prompt = f"""
    **Οδηγίες:**
    1. Ανάλυσε το κείμενο που παρέχεται, λαμβάνοντας υπόψη το γενικό πλαίσιο, τις λεπτομέρειες και την πρόθεση του χρήστη.
    2. Επίλεξε μία **Κατηγορία** από τη λίστα των διαθέσιμων Κατηγοριών που ταιριάζει καλύτερα με το κείμενο.
    3. Για την επιλεγμένη Κατηγορία, επέλεξε την αντίστοιχη **Υποκατηγορία** που να περιγράφει πιο συγκεκριμένα το περιεχόμενο του κειμένου.
    4. Στη συνέχεια, για την επιλεγμένη Υποκατηγορία, επέλεξε την κατάλληλη **Υπο-υποκατηγορία** που σχετίζεται με τις πιο εξειδικευμένες λεπτομέρειες του κειμένου.
    5. Εάν το κείμενο δεν ταιριάζει απόλυτα με καμία υπάρχουσα κατηγορία ή υποκατηγορία, απάντησε με "Δεν βρέθηκε".
    6. **Είναι υποχρεωτικό να συμπεριλάβεις πάντα την ενότητα "Αναφορά Αποτελεσμάτων" στο τέλος της απάντησης, με την κατηγοριοποίηση του κειμένου, όπως περιγράφεται παρακάτω.**
    7. Λάβε υπόψιν σου και το σκόρ από το document με το μεγαλύτερο σκόρ.
    
    **Highest-Scoring Document (Priority):**
    {highest_doc_info}

    **Διαθέσιμες Κατηγορίες:**
    Κατηγορίες: {json.dumps(existing_categories, ensure_ascii=False)}
    Υποκατηγορίες: {json.dumps(existing_subcategories, ensure_ascii=False)}
    Υπο-υποκατηγορίες: {json.dumps(existing_sub_subcategories, ensure_ascii=False)}

    **Παραδείγματα:**
    {json.dumps([{"Category": doc["Category"], "Sub-Category": doc["Sub-Category"], "Sub-sub-Category": doc["Sub-sub-Category"], "Description": doc["Description"]} for doc in documents], ensure_ascii=False)}

    **Ερώτημα Χρήστη:**
    {query}

    **Αναφορά Αποτελεσμάτων:**
    **Category**: [Επιλέξτε μία από τις υπάρχουσες κατηγορίες]
    **Sub-Category**: [Επιλέξτε μία από τις υπάρχουσες υποκατηγορίες]
    **Sub-Sub-Category**: [Επιλέξτε μία από τις υπάρχουσες υπο-υποκατηγορίες]
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
                        "Always prioritize the highest-scoring document for classification."
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
        category, subcategory, subsubcategory = parse_openai_response(response['choices'][0]['message']['content'])
        logger.info(f"Classification result: Category - {category}, Sub-Category - {subcategory}, Sub-sub-Category - {subsubcategory}")

    except Exception as e:
        # Log the error and set default classification
        logger.error(f"Error in OpenAI classification: {e}")
        category, subcategory, subsubcategory = "Unknown1", "Unknown2", "Unknown3"

    return category, subcategory, subsubcategory


def parse_openai_response(response_text):
    """
    Parses the OpenAI response text to extract Category, Sub-Category, and Sub-Sub-Category.
    Uses regex without look-behind to avoid the 'fixed-width' error.
    """
    try:
        # Log the full response text for debugging purposes
        logger.debug(f"Full OpenAI response: {response_text}")
        
        # Regular expressions to capture the categories without look-behind
        category_match = re.search(r"\*\*Category\*\*:?\s*([^\n]+)", response_text)
        subcategory_match = re.search(r"\*\*Sub-Category\*\*:?\s*([^\n]+)", response_text)
        subsubcategory_match = re.search(r"\*\*Sub-Sub-Category\*\*:?\s*([^\n]+)", response_text)
        
        # Extract the values or use "Unknown" if not found
        category = category_match.group(1).strip() if category_match else "Unknown"
        subcategory = subcategory_match.group(1).strip() if subcategory_match else "Unknown"
        subsubcategory = subsubcategory_match.group(1).strip() if subsubcategory_match else "Unknown"
        
        # Log warnings if any categories are missing
        if category == "Unknown":
            logger.warning("Category not found in response")
        if subcategory == "Unknown":
            logger.warning("Sub-Category not found in response")
        if subsubcategory == "Unknown":
            logger.warning("Sub-Sub-Category not found in response")
        
        return category, subcategory, subsubcategory
    except Exception as e:
        logger.error(f"Error parsing response: {e}")
        return "Unknown", "Unknown", "Unknown"
