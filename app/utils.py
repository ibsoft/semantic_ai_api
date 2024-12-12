import openai
import json
import time
import tiktoken  # Import tiktoken for counting tokens
import requests  # Import requests for HTTP requests
from .config import Config
import logging
from elasticsearch import Elasticsearch
import re




# Initialize OpenAI API key and logger
openai.api_key = Config.OPENAI_API_KEY
logger = logging.getLogger()
logger.info("Application started and logging configured.")

# Token counting function using tiktoken
def count_tokens(text):
    encoding = tiktoken.get_encoding("cl100k_base")  # Choose the encoding for your model
    tokens = encoding.encode(text)
    return len(tokens)

# Function to get embedding using OLLAMA API
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

# Function to classify the query
def classify_text(query, es):
    start_time = time.time()
    logger.debug(f"Classifying text: {query}")

    # Calculate tokens for the input query before making the request
    input_tokens = count_tokens(query)
    logger.info(f"Token count for query: {input_tokens} tokens")

    embedding = get_embedding(query)
    if not embedding:
        logger.warning("Failed to generate query embedding")
        raise ValueError("Failed to generate query embedding")

    # Fetch hierarchical data using aggregations from Elasticsearch
    fetch_all_query = {
        "size": 0,  # No need for hits, only aggregations
        "aggs": {
            "supercategories": {
                "terms": {
                    "field": "SUPERCATEGORY.keyword",
                    "size": 1000
                },
                "aggs": {
                    "categories": {
                        "terms": {
                            "field": "CATEGORY.keyword",
                            "size": 1000
                        },
                        "aggs": {
                            "subcategories": {
                                "terms": {
                                    "field": "SUBCATEGORY.keyword",
                                    "size": 1000
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    try:
        # Perform the search to fetch all aggregations
        response = es.search(index="new_skl_categories_index_v2", body=fetch_all_query)
        supercategory_agg = response['aggregations']['supercategories']['buckets']

        # Extract hierarchical data (supercategories, categories, subcategories)
        hierarchical_data = {}
        for supercategory in supercategory_agg:
            supercategory_name = supercategory['key']
            hierarchical_data[supercategory_name] = {}

            for category in supercategory['categories']['buckets']:
                category_name = category['key']
                hierarchical_data[supercategory_name][category_name] = []

                # Handle cases where subcategories might be "None"
                for subcategory in category['subcategories']['buckets']:
                    subcategory_name = subcategory['key']
                    hierarchical_data[supercategory_name][category_name].append(subcategory_name if subcategory_name != "None" else None)

        logger.info(f"Hierarchical data: {json.dumps(hierarchical_data, indent=2)}")
    except Exception as e:
        logger.error(f"Error while searching Elasticsearch: {e}")
        hierarchical_data = {}
        
    #formatted_hierarchical_data = json.dumps(hierarchical_data, indent=2)
    #print(formatted_hierarchical_data)

    # Similarity threshold for vector search
    SIMILARITY_THRESHOLD = Config.EXAMPLES_SIMILARITY_THRESHOLD

    # Vector search for similar documents (categorization)
    vector_search_query = {
        "knn": {
            "field": "embedding",
            "query_vector": embedding,
            "k": 5,
            "num_candidates": 10
        }
    }

    try:
        # Perform the vector search query
        vector_search_response = es.search(index="skl_examples_index", body=vector_search_query)

        # Extract vector search results
        vector_search_examples = [
            {
                "TITLE": hit["_source"].get("TITLE", ""),
                "MESSAGE": hit["_source"].get("MESSAGE", ""),
                "SUPERCATEGORY": hit["_source"].get("SUPERCATEGORY", ""),
                "CATEGORY": hit["_source"].get("CATEGORY", ""),
                "SUBCATEGORY": hit["_source"].get("SUBCATEGORY", ""),
                 "_score": hit.get("_score", 0) 
            }
            for hit in vector_search_response["hits"]["hits"]
        ]
        logger.info(f"Found {len(vector_search_examples)} vector search examples")
    except Exception as e:
        logger.error(f"Error performing vector search: {e}")
        vector_search_examples = []


    # Log the scores of each example
    for example in vector_search_examples:
        logger.info(f"Score for example with  {example.get('TITLE', 'N/A')}: {example.get('_score', 0)}")

    # Filter vector search examples based on similarity threshold
    relevant_vector_search_examples = [
    example for example in vector_search_examples if example["_score"] >= SIMILARITY_THRESHOLD
    ]

    # If no relevant examples are found, set it to None
    if not relevant_vector_search_examples:
        logging.info(f"No relevant example hit config score {Config.EXAMPLES_SIMILARITY_THRESHOLD}, Setting to None!")
        relevant_vector_search_examples = None
    else:
        logging.info(f"We've got hit. Passing example to model")

    elapsed_time = round(time.time() - start_time, 2)

    # Call the classify function with the new document fields
    try:
        supercategory, category, subcategory = classify(query, hierarchical_data, relevant_vector_search_examples)
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        supercategory, category, subcategory = None, None, None

    logger.info(f"Classification completed in {elapsed_time} seconds")

    return {
        "supercategory": supercategory,
        "category": category,
        "subcategory": subcategory
    }, elapsed_time

# Function to classify based on the query, hierarchical data, and vector search examples
def classify(query, hierarchical_data, vector_search_examples):
    if Config.USE_EXAMPLES:
        logger.info("Using Examples")
        prompt = f"""
        Στόχος σου είναι να Αναλύσεις μια λίστα κατηγοριών με υποκατηγορίες, οι οποίες οργανώνονται σε αυστηρή ιεραρχία:

        1. **Υπερκατηγορίες**: Κάθε υπερκατηγορία περιέχει πολλές κατηγορίες.
        2. **Κατηγορίες**: Κάθε κατηγορία περιέχει πολλές υποκατηγορίες.

        **Η αποστολή σου** όταν σου δοθεί ένα ερώτημα χρήστη είναι να:
        1. **Αναγνωρίσεις τη δομή υπερκατηγορίας, κατηγορίας και υποκατηγορίας** από τις προκαθορισμένες λίστες.
        2. **Εντοπίσε την πιο σχετική επιλογή** από τις προκαθορισμένες λίστες με βάση το ερώτημα του χρήστη.
        3. **Μην επιλέγεις την πρώτη επιλογή** στην ιεραρχία, αλλά την επιλογή που είναι πιο σχετική με βάση τα συμφραζόμενα ή τις λέξεις-κλειδιά που δίνονται στο ερώτημα.
        4. Εάν καμία υποκατηγορία δεν είναι σχετική, επίλεξε "Καμία".

        **Προκαθορισμένες Λίστες (εξουσιοδοτημένες):**
        {json.dumps(hierarchical_data, indent=2, ensure_ascii=False)}

        **Ερώτημα Χρήστη:** {query}
        
        **Παραδείγματα σχετικά με το ερώτημα του χρήστη. (Αν υπάρχουν) Δες αν σε βοηθάνε να κατηγοριοποιήσεις:**
        {json.dumps(vector_search_examples, indent=2)}

        **Μορφή εξόδου (αυστηρά απαιτούμενη):**
        - Supercategory: [Επίλεξε μία από τις προκαθορισμένες υπερκατηγορίες, εάν είναι σχετική· διαφορετικά "Καμία"]
        - Category: [Επίλεξε μία από τις προκαθορισμένες κατηγορίες κάτω από την επιλεγμένη υπερκατηγορία, εάν είναι σχετική· διαφορετικά "Καμία"]
        - Sub-Category: [Επίλεξε μία από τις προκαθορισμένες υποκατηγορίες κάτω από την επιλεγμένη κατηγορία, εάν είναι σχετική· διαφορετικά "Καμία"]

        Για παράδειγμα, αν το ερώτημα του χρήστη αναφέρει "ακονιστήρι" ή "τροχός", επίλεξε την υποκατηγορία **ΑΚΟΝΙΣΤΗΡΙ** κάτω από την κατηγορία **ΜΗΧΑΝΕΣ ΚΟΠΗΣ** στην **ΥΠΕΡΚΑΤΗΓΟΡΙΑ 5.ΣΥΣΚΕΥΕΣ / ΜΗΧΑΝΕΣ**, επειδή είναι είναι σημασιολογικά σχετική.
"""

    else:
        logger.info("NOT using Examples")
        prompt = f"""
        Στόχος σου είναι να Αναλύσεις μια λίστα κατηγοριών με υποκατηγορίες, οι οποίες οργανώνονται σε αυστηρή ιεραρχία:

        1. **Υπερκατηγορίες**: Κάθε υπερκατηγορία περιέχει πολλές κατηγορίες.
        2. **Κατηγορίες**: Κάθε κατηγορία περιέχει πολλές υποκατηγορίες.

        **Η αποστολή σου** όταν σου δοθεί ένα ερώτημα χρήστη είναι να:
        1. **Αναγνωρίσεις τη δομή υπερκατηγορίας, κατηγορίας και υποκατηγορίας** από τις προκαθορισμένες λίστες.
        2. **Εντοπίσε την πιο σχετική επιλογή** από τις προκαθορισμένες λίστες με βάση το ερώτημα του χρήστη.
        3. **Μην επιλέγεις την πρώτη επιλογή** στην ιεραρχία, αλλά την επιλογή που είναι πιο σχετική με βάση τα συμφραζόμενα ή τις λέξεις-κλειδιά που δίνονται στο ερώτημα.
        4. Εάν καμία υποκατηγορία δεν είναι σχετική, επίλεξε "Καμία".

        **Προκαθορισμένες Λίστες (εξουσιοδοτημένες):**
        {json.dumps(hierarchical_data, indent=2, ensure_ascii=False)}

        **Ερώτημα Χρήστη:** {query}
        
        **Μορφή εξόδου (αυστηρά απαιτούμενη):**
        - Supercategory: [Επίλεξε μία από τις προκαθορισμένες υπερκατηγορίες]
        - Category: [Επίλεξε μία από τις προκαθορισμένες κατηγορίες κάτω από την επιλεγμένη υπερκατηγορία]
        - Sub-Category: [Επίλεξε μία από τις προκαθορισμένες υποκατηγορίες κάτω από την επιλεγμένη κατηγορία, εάν είναι σχετική· διαφορετικά "Καμία"]

        Για παράδειγμα, αν το ερώτημα του χρήστη αναφέρει "ακονιστήρι" ή "τροχός", επίλεξε την υποκατηγορία **ΑΚΟΝΙΣΤΗΡΙ** κάτω από την κατηγορία **ΜΗΧΑΝΕΣ ΚΟΠΗΣ** στην **ΥΠΕΡΚΑΤΗΓΟΡΙΑ 5.ΣΥΣΚΕΥΕΣ / ΜΗΧΑΝΕΣ**, επειδή είναι είναι σημασιολογικά σχετική.
"""

    try:
        response = openai.ChatCompletion.create(
            model=Config.MODEL,
            messages=[
                {"role": "system", "content": "You are a strict classifier. Classify the query into one of the existing supercategories, categories, and subcategories."},
                {"role": "user", "content": prompt}
            ]
        )
        classification_response = response['choices'][0]['message']['content'].strip()

        # Ensure the response contains valid categories, else set them to "None"
        if not classification_response:
            logger.error("Received empty response from OpenAI")
            return "None", "None", "None"

         # Log the response details including token usage
        usage_info = response.get('usage', {})
        logger.info(f"Response from OpenAI received for query: {query}")
        logger.info(f"Total tokens used: {usage_info.get('total_tokens', 'N/A')}")
        logger.info(f"Prompt tokens: {usage_info.get('prompt_tokens', 'N/A')}")
        logger.info(f"Completion tokens: {usage_info.get('completion_tokens', 'N/A')}")
        logger.debug(f"Response content: {response['choices'][0]['message']['content']}")
        logger.debug(f"AI Classification Response: {classification_response}")

        # Parse the response to remove redundant prefixes
        supercategory, category, subcategory = parse_classification_response(classification_response)

    except Exception as e:
        logger.error(f"Error during OpenAI API call: {e}")
        supercategory, category, subcategory = "None", "None", "None"

    return supercategory, category, subcategory


def parse_classification_response(classification_response):
    """
    Parses the AI classification response and separates the supercategory, category, and subcategory.
    """
    # Log the raw response for debugging purposes
    logger.debug(f"Raw classification response: {classification_response}")

    # Define expected labels for classification
    labels = {
        "supercategory": "Supercategory: ",
        "category": "Category: ",
        "subcategory": "Sub-Category: "
    }

    # Initialize the fields
    supercategory = "None"
    category = "None"
    subcategory = "None"

    # Strip extra spaces and split the response into lines
    lines = classification_response.strip().split("\n")
    logger.debug(f"Parsed lines: {lines}")

    # Process each line and assign values to supercategory, category, and subcategory
    for line in lines:
        line = line.strip().lstrip('-').strip()  # Remove leading '-' and extra whitespace

        # Remove '**' that are present around the labels
        line = line.replace('**', '').strip()

        # Use regex to extract the classification values
        for key, label in labels.items():
            # Create a regex pattern to capture everything after the label
            pattern = re.compile(f"^{re.escape(label)}(.*)")
            match = pattern.match(line)

            if match:
                value = match.group(1).strip().strip('"')
                # Assign the matched value to the correct field
                if key == "supercategory":
                    supercategory = value
                elif key == "category":
                    category = value
                elif key == "subcategory":
                    subcategory = value

    logger.info(f"Supercategory: {supercategory}, Category: {category}, Subcategory: {subcategory}")
    
    return supercategory, category, subcategory