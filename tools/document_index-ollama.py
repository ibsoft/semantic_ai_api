import requests
import json
from elasticsearch import Elasticsearch

# Elasticsearch setup
es = Elasticsearch(["http://localhost:9200"])

# Ollama API setup
OLLAMA_API_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "paraphrase-multilingual"


def get_embedding(text):
    """
    Get the embedding for the given text using the Ollama API.
    """
    headers = {"Content-Type": "application/json"}
    payload = {"model": OLLAMA_MODEL, "prompt": text}
    try:
        response = requests.post(
            OLLAMA_API_URL, headers=headers, json=payload, timeout=30
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("embedding", None)
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except (json.decoder.JSONDecodeError, KeyError):
        print("Error decoding JSON response or missing 'embedding' key.")
        return None


def create_index():
    """
    Create the 'categories_db' index with a specific mapping for categories and embeddings.
    """
    index_mapping = {
        "mappings": {
            "properties": {
                "Category": {"type": "keyword"},  # Category field mapping
                "embedding": {
                    "type": "dense_vector",
                    "dims": 768  # Correct embedding dimensions
                }
            }
        }
    }
    # Delete index if it exists
    es.indices.delete(index="categories_db", ignore=[400, 404])
    es.indices.create(index="categories_db", body=index_mapping, ignore=400)


def index_documents(data):
    """
    Index the documents from the dataset, creating embeddings and storing them in Elasticsearch.
    """
    # Extract the dataset from the JSON
    dataset = data.get("dataset", [])  # Safely get the 'dataset' key, defaulting to an empty list

    for i, doc in enumerate(dataset):  # Loop through the extracted dataset
        category = doc.get("Category")  # Safely extract the 'Category' key
        
        if not category:
            print(f"Skipping document {i} due to missing category.")
            continue

        # Generate embedding using the Category field
        embedding = get_embedding(category)  # Use category as the input for the embedding
        
        if not embedding or len(embedding) != 768:
            print(f"Skipping document {i} due to invalid embedding.")
            continue

        document = {
            "Category": category,  # Store category name only
            "embedding": embedding
        }

        try:
            # Index document in Elasticsearch under the 'categories_db' index
            es.index(index="categories_db", id=i, document=document)
            print(f"Document {i} indexed successfully.")
        except Exception as e:
            print(f"Failed to index document {i}: {e}")



if __name__ == "__main__":
    # Load dataset from a JSON file
    with open("categories.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Create the index
    create_index()
    
    # Index the documents
    index_documents(data)
    
    print("All documents indexed successfully!")
