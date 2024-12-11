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
            "SUPERCATEGORY": {"type": "text"},
            "CATEGORY": {"type": "text"},
            "CATEGORY_CODE": {"type": "keyword"},
            "SUBCATEGORY": {"type": "text"},
            "SUBCATEGORY_CODE": {"type": "keyword"},
            "SIGNIFICANCE": {"type": "keyword"},
            "TCID": {"type": "integer"},
            "embedding": {"type": "dense_vector", "dims": 768},
        }
    }
}

    # Delete index if it exists
    es.indices.delete(index="skl_categories_index", ignore=[400, 404])
    es.indices.create(index="skl_categories_index", body=index_mapping, ignore=400)


def index_documents(data):
    for i, doc in enumerate(data["CATEGORIES"]):
        super_category = doc.get("SUPERCATEGORY", "")
        category = doc.get("CATEGORY", "")
        category_code = doc.get("CATEGORY_CODE", "")
        sub_category = doc.get("SUBCATEGORY", "")
        sub_category_code = doc.get("SUBCATEGORY_CODE", "")
        significance = doc.get("SIGNIFICANCE", "")
        tcid = doc.get("TCID", 0)

        # Generate embedding
        embedding = get_embedding(super_category +" "+ category +" "+ sub_category +" "+ significance)
        if not embedding or len(embedding) != 768:
            print(f"Skipping document {i} due to invalid embedding.")
            continue

        document = {
            "SUPERCATEGORY": super_category,
            "CATEGORY": category,
            "CATEGORY_CODE": category_code,
            "SUBCATEGORY": sub_category,
            "SUBCATEGORY_CODE": sub_category_code,
            "SIGNIFICANCE": significance,
            "TCID": int(tcid),
            "embedding": embedding,
        }

        try:
            es.index(index="skl_categories_index", id=i, document=document)
            print(f"Document {i} indexed successfully.")
        except Exception as e:
            print(f"Failed to index document {i}: {e}")


if __name__ == "__main__":
    with open("documents.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    create_index()
    index_documents(data)
    print("All documents indexed successfully!")
