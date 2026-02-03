import csv
import os
from typing import Any

import vertexai
from dotenv import load_dotenv
from google.cloud import bigquery, storage
from vertexai.language_models import TextEmbeddingModel

load_dotenv()

project_id = os.getenv("PROJECT_ID")
bucket_name = os.getenv("BUCKET_NAME")
category_blob = os.getenv("CATEGORY_BLOB")
category_table = os.getenv("CATEGORY_TABLE")

vertexai.init(project=project_id, location="us-central1")
model = TextEmbeddingModel.from_pretrained("text-embedding-004")


def generate_embedding(text: str) -> Any:
    """Generate embeddings of the text using Vertex AI"""
    embeddings = model.get_embeddings([text])
    return embeddings[0].values


def save_to_bigquery(
    category: str,
    description: str,
    embedding: list,
) -> None:
    """Save category, description and embedding in BigQuery"""
    if not category_table:
        msg_error = "CATEGORY_TABLE environment variable is not set"
        raise ValueError(msg_error)

    client = bigquery.Client()

    rows_to_insert = [
        {
            "category": category,
            "description": description,
            "embedding": embedding,
        },
    ]

    errors = client.insert_rows_json(category_table, rows_to_insert)
    if errors:
        msg = f"Error in BigQuery: {errors}"
        raise Exception(msg)

    print(f"Save: {category}")


def process_category(
    category: str,
    description: str,
) -> None:
    """Process to generate category embeddings"""
    embedding = generate_embedding(description)
    save_to_bigquery(category, description, embedding)


def get_categories_from_gcs() -> list[dict]:
    """Extract categories from GCS CSV"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(category_blob)
    content = blob.download_as_text()

    reader = csv.DictReader(content.splitlines())
    return [
        {"category": row["category"], "description": row["description"]}
        for row in reader
    ]


if __name__ == "__main__":
    print("Extract categories from GCS...")
    categories = get_categories_from_gcs()

    for i, item in enumerate(categories, 1):
        print(f"[{i}/{len(categories)}] {item['category']}")
        try:
            process_category(item["category"], item["description"])
        except (ValueError, OSError) as e:
            print(f"Error: {e}")

    print("\n¡Successful Process!")
