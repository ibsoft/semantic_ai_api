import requests
import json
from elasticsearch import Elasticsearch

# Elasticsearch setup
es = Elasticsearch(["http://192.168.1.4:9200"])

# Ollama API setup
OLLAMA_API_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "paraphrase-multilingual"

def get_embedding(text):
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
    index_mapping = {
        "mappings": {
            "properties": {
                "TITLE": {"type": "text"},
                "MESSAGE": {"type": "text"},
                "SUPERCATEGORY": {"type": "text"},
                "CATEGORY": {"type": "text"},
                "SUBCATEGORY": {"type": "text"},
                "TCID": {"type": "integer"},
                "embedding": {"type": "dense_vector", "dims": 768},
            }
        }
    }

    # Delete index if it exists
    es.indices.delete(index="skl_examples_index", ignore=[400, 404])
    es.indices.create(index="skl_examples_index", body=index_mapping, ignore=400)

def index_documents(data):
    for i, doc in enumerate(data):
        title = doc.get("Title", "")
        message = doc.get("message", "")
        super_category = doc.get("Super-Category", "")
        category = doc.get("Category", "")
        sub_category = doc.get("Sub-Category", "")

        # Generate embedding for combined fields
        embedding_text = f"{title} {message} {super_category} {category} {sub_category}"
        embedding = get_embedding(embedding_text)
        if not embedding or len(embedding) != 768:
            print(f"Skipping document {i} due to invalid embedding.")
            continue

        document = {
            "TITLE": title,
            "MESSAGE": message,
            "SUPERCATEGORY": super_category,
            "CATEGORY": category,
            "SUBCATEGORY": sub_category,
            "TCID": i,  # Using index as a placeholder for TCID
            "embedding": embedding,
        }

        try:
            es.index(index="skl_examples_index", id=i, document=document)
            print(f"Document {i} indexed successfully.")
        except Exception as e:
            print(f"Failed to index document {i}: {e}")

if __name__ == "__main__":
    with open("examples.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    create_index()
    index_documents(data)
    print("All documents indexed successfully!")
