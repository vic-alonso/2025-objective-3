import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from google.cloud import bigquery

START_PAGE = 2


def get_categories_from_bigquery() -> list:
    client = bigquery.Client()
    query = (
        "SELECT category, url FROM `lineage-alt-test.vic_objective_3.category-table`"
    )
    results = client.query(query).result()
    return [(row.category, row.url) for row in results]


def get_aws_ml_blogs(category: str, base_url: str) -> list:
    blogs = []

    for page in range(START_PAGE, 7):
        url = base_url if page == START_PAGE else f"{base_url}page/{page - 1}/"
        response = requests.get(url, timeout=60)
        soup = BeautifulSoup(response.content, "html.parser")

        articles = soup.find_all("article", class_="blog-post")

        if not articles:
            continue

        for article in articles:
            title_tag = article.find("h2", class_="blog-post-title")
            link_tag = title_tag.find("a") if title_tag else None
            link = link_tag["href"] if link_tag else None
            title = title_tag.get_text(strip=True) if title_tag else None

            if title and link:
                blogs.append({"title": title, "link": link, "category": category})

    return blogs


if __name__ == "__main__":
    categories = get_categories_from_bigquery()

    for category, url in categories:
        blogs = get_aws_ml_blogs(category, url)
        filename = Path(f"../json-files/{category}-articles.json")
        with filename.open("w", encoding="utf-8") as f:
            json.dump(blogs, f, indent=2, ensure_ascii=False)
        print(f"Saved {category}")
