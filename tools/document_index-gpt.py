import json
import hashlib
from elasticsearch import Elasticsearch
import openai

# Elasticsearch configuration
es_host = "http://192.168.7.10:9200"  # Replace with your Elasticsearch host
index_name = "documents_index"

# OpenAI API Key
openai.api_key = "your_open_ai_api_key"

# Initialize Elasticsearch client
es = Elasticsearch([es_host])

# Ensure Elasticsearch index exists


def create_index_if_not_exists():
    mapping = {
        "mappings": {
            "properties": {
                "Description": {"type": "text"},
                "Category": {"type": "keyword"},
                "Sub-Category": {"type": "keyword"},
                "hash": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 1536  # Ensure this matches the embedding model's dimensions
                }
            }
        }
    }

    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body=mapping)
        print(f"Created Elasticsearch index: {index_name}")
    else:
        print(f"Elasticsearch index {index_name} already exists.")

# Generate a hash to detect unchanged documents


def generate_document_hash(doc):
    hash_source = f"{doc['Description']}{doc['Category']}{doc['Sub-Category']}"
    return hashlib.md5(hash_source.encode()).hexdigest()

# Check if the document is already indexed and unchanged


def is_document_unchanged(doc):
    doc_hash = generate_document_hash(doc)
    search_query = {
        "query": {
            "term": {
                "hash": doc_hash
            }
        }
    }

    try:
        response = es.search(index=index_name, body=search_query)
        return response['hits']['total']['value'] > 0
    except Exception as e:
        print(f"Error checking document hash in Elasticsearch: {e}")
        return False

# Generate embeddings using OpenAI Python 1.0.0 API


def get_embedding(text):
    try:
        # Request embedding using OpenAI's embeddings API
        response = openai.embeddings.create(
            model="text-embedding-ada-002",  # You can change the model if needed
            input=text
        )
        # Correct way to access the embedding data
        # This accesses the embedding from the first item in the data list
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding for text: {text[:30]}...: {e}")
        return None

# Index document into Elasticsearch


def index_document_with_embedding(doc):
    embedding = get_embedding(doc['Description'])
    if embedding is None:
        print(
            f"Failed to generate embedding for document: {doc['Description']}")
        return

    doc_with_embedding = {
        "Description": doc["Description"],
        "Category": doc["Category"],
        "Sub-Category": doc["Sub-Category"],
        "hash": generate_document_hash(doc),
        "embedding": embedding
    }

    try:
        es.index(index=index_name, body=doc_with_embedding)
        print(f"Successfully indexed document: {doc['Description']}")
    except Exception as e:
        print(f"Error indexing document {doc['Description']}: {e}")

# Process documents from JSON file and index them


def process_documents_on_startup():
    try:
        with open("documents.json", "r", encoding="utf-8") as file:
            documents = json.load(file)
            # Adjusted to use "dataset" key
            for doc in documents.get("dataset", []):
                try:
                    if not is_document_unchanged(doc):
                        index_document_with_embedding(doc)
                        print(f"Indexed document: {doc['Description']}")
                    else:
                        print(
                            f"Document unchanged, skipping: {doc['Description']}")
                except Exception as e:
                    print(
                        f"Error processing document {doc['Description']}: {e}")
    except FileNotFoundError:
        print("documents.json file not found. No documents indexed.")
    except Exception as e:
        print(f"Error reading documents.json: {e}")


# Main startup process
if __name__ == "__main__":
    create_index_if_not_exists()
    process_documents_on_startup()
