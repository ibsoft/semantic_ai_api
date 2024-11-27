import requests
import json
from elasticsearch import Elasticsearch

# Elasticsearch setup
es = Elasticsearch(["http://localhost:9200"])

# Ollama API setup
OLLAMA_API_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "paraphrase-multilingual"


def get_embedding(text):
    headers = {"Content-Type": "application/json"}
    payload = {"model": OLLAMA_MODEL, "prompt": text}
    try:
        response = requests.post(
            OLLAMA_API_URL, headers=headers, json=payload, timeout=30)
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
    index_mapping = {
        "mappings": {
            "properties": {
                "Description": {"type": "text"},
                "Category": {"type": "keyword"},
                "Sub-Category": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 768  # Replace with correct dimensions
                }
            }
        }
    }
    # Delete index if it exists
    es.indices.delete(index="documents", ignore=[400, 404])
    es.indices.create(index="documents", body=index_mapping, ignore=400)


def index_documents(data):
    for i, doc in enumerate(data["dataset"]):
        description = doc["Description"]
        category = doc["Category"]
        sub_category = doc["Sub-Category"]

        # Generate embedding
        embedding = get_embedding(description)
        # Replace 768 with actual dimensions
        if not embedding or len(embedding) != 768:
            print(f"Skipping document {i} due to invalid embedding.")
            continue

        document = {
            "Description": description,
            "Category": category,
            "Sub-Category": sub_category,
            "embedding": embedding
        }

        try:
            es.index(index="documents", id=i, document=document)
            print(f"Document {i} indexed successfully.")
        except Exception as e:
            print(f"Failed to index document {i}: {e}")


if __name__ == "__main__":
    with open("documents.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    create_index()
    index_documents(data)
    print("All documents indexed successfully!")
