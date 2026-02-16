import functions_framework
import numpy as np
import vertexai
from flask import Request
from google.cloud import bigquery
from vertexai.language_models import TextEmbeddingModel

msg_phrase = {"error": "It is needed the parameter 'phrase'"}
msg_article = {"error": "No articles found"}

# Initialization Vertex AI
vertexai.init(project="lineage-alt-test", location="us-central1")


class ModelCache:
    model: TextEmbeddingModel | None = None
    @classmethod
    def get_model(cls) -> TextEmbeddingModel:
        if cls.model is None:
            cls.model = TextEmbeddingModel.from_pretrained("text-embedding-004")
        return cls.model


def find_top_categories(
    phrase_embedding: np.ndarray, client: bigquery.Client, top_n: int = 3,
) -> list[str]:
    query = """
        SELECT category, embedding
        FROM `lineage-alt-test.vic_objective_3.category-table`
    """
    rows = client.query(query).result()
    categories = []
    for row in rows:
        category_embedding = np.array(row.embedding)
        similarity = np.dot(phrase_embedding, category_embedding) / (
            np.linalg.norm(phrase_embedding) * np.linalg.norm(category_embedding)
        )
        categories.append((row.category, similarity))
    categories.sort(key=lambda x: x[1], reverse=True)
    top_categories = [cat for cat, _ in categories[:top_n]]
    print(f"Top {top_n} categories: {top_categories}")
    return top_categories


@functions_framework.http
def recommend_article(request: Request) -> tuple[dict, int]:
    phrase = request.args.get("phrase")
    if not phrase:
        return msg_phrase, 400
    model = ModelCache.get_model()
    embeddings = model.get_embeddings([phrase])
    phrase_embedding = np.array(embeddings[0].values)
    client = bigquery.Client()
    top_categories = find_top_categories(phrase_embedding, client)
    query = """
        SELECT title, url, embedding
        FROM `lineage-alt-test.vic_objective_3.article-embeddings`
    """
    if top_categories:
        categories_str = "', '".join(top_categories)
        query += f" WHERE category IN ('{categories_str}')"
    rows = client.query(query).result()
    best_article = None
    max_similarity = -1
    for row in rows:
        article_embedding = np.array(row.embedding)
        similarity = np.dot(phrase_embedding, article_embedding) / (
            np.linalg.norm(phrase_embedding) * np.linalg.norm(article_embedding)
        )
        if similarity > max_similarity:
            max_similarity = similarity
            best_article = {
                "title": row.title,
                "url": row.url,
                "similarity": float(similarity),
            }
    print(f"Best article: {best_article} with similarity: {max_similarity}")
    return (best_article, 200) if best_article else (msg_article, 404)
