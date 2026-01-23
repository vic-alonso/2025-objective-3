import json

import requests
from bs4 import BeautifulSoup


def get_aws_ml_blogs() -> list:
    blogs = []
    page = 2

    url = f"https://aws.amazon.com/blogs/machine-learning/page/{page}/"
    response = requests.get(url, timeout=60)
    soup = BeautifulSoup(response.content, "html.parser")

    articles = soup.find_all("article", class_="blog-post")

    if not articles:
        return blogs

    for article in articles:
        title_tag = article.find("h2", class_="blog-post-title")
        link_tag = title_tag.find("a") if title_tag else None
        link = link_tag["href"] if link_tag else None
        title = title_tag.get_text(strip=True) if title_tag else None

        if title and link:
            blogs.append({"title": title, "link": link})

    return blogs


if __name__ == "__main__":
    blogs = get_aws_ml_blogs()

    with open("../json-files/aws-ml-articles.json", "w", encoding="utf-8") as f:
        json.dump(blogs, f, indent=2, ensure_ascii=False)
