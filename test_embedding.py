import os
import vertexai
from dotenv import load_dotenv
from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel

load_dotenv()

project_id = os.getenv("PROJECT_ID")
dataset_id = os.getenv("DATASET_ID")
table_id = os.getenv("TABLE_ID")

vertexai.init(project=project_id, location="us-central1")
model = TextEmbeddingModel.from_pretrained("text-embedding-004")

# Test con un texto simple
text = "How AutoScout24 built a Bot Factory to standardize AI agent development with Amazon Bedrock"
embeddings = model.get_embeddings([text])
embedding_values = embeddings[0].values

print(f"Embedding dimensions: {len(embedding_values)}")

# Guardar en BigQuery
client = bigquery.Client()
table_ref = f"{project_id}.{dataset_id}.{table_id}"

rows_to_insert = [{
    "url": "https://test.com",
    "title": "Test Article",
    "embedding": embedding_values,
}]

errors = client.insert_rows_json(table_ref, rows_to_insert)
if errors:
    print(f"Error: {errors}")
else:
    print("✓ Successfully saved to BigQuery!")
