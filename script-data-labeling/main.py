import json
import os
from typing import Any

import requests
import vertexai
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google.cloud import bigquery, storage
from vertexai.language_models import TextEmbeddingModel

load_dotenv()

project_id = os.getenv("PROJECT_ID")
bucket_name = os.getenv("BUCKET_NAME")
dataset_id = os.getenv("DATASET_ID")
table_id = os.getenv("TABLE_ID")

vertexai.init(project=project_id, location="us-central1")
model = TextEmbeddingModel.from_pretrained("text-embedding-004")


def extract_content(url: str) -> str:
    """Extract URL content"""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    return soup.get_text(separator=" ", strip=True)


def generate_embedding(text: str) -> Any:
    """Generate embeddings of the text using Vertex AI"""
    embeddings = model.get_embeddings([text])
    return embeddings[0].values


def save_to_bigquery(
    url: str,
    title: str,
    embedding: list,
) -> None:
    """Save url, title and embedding in BigQuery"""
    client = bigquery.Client()
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    rows_to_insert = [
        {
            "url": url,
            "title": title,
            "embedding": embedding,
        },
    ]

    errors = client.insert_rows_json(table_ref, rows_to_insert)
    if errors:
        msg = f"Error in BigQuery: {errors}"
        raise Exception(msg)

    print(f"Save: {title}")


def process_url(
    url: str,
    title: str,
) -> None:
    """Process to generate url embeddings"""
    content = extract_content(url)
    embedding = generate_embedding(content)
    save_to_bigquery(url, title, embedding)


def get_urls_from_gcs() -> tuple[list[str], list[str]]:
    """Extract the URLs from the bucket to GCS"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix="")

    urls = []
    titles = []
    for blob in blobs:
        if not blob.name.endswith(".json"):
            continue

        content = blob.download_as_text()
        data = json.loads(content)

        items = data if isinstance(data, list) else [data]
        for item in items:
            if "link" in item:
                urls.append(item["link"])
            if "title" in item:
                titles.append(item["title"])

    return urls, titles


if __name__ == "__main__":
    print("Extract URLs from the bucket...")
    urls, titles = get_urls_from_gcs()

    for i, (url, title) in enumerate(zip(urls, titles, strict=True), 1):
        print(f"[{i}/{len(urls)}] {title}")
        try:
            process_url(url, title)
        except (requests.RequestException, ValueError, OSError) as e:
            print(f"Error: {e}")

    print("\n¡Successful Process!")
