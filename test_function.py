import os

import requests
from dotenv import load_dotenv

load_dotenv()

cloud_function_url = os.getenv("CLOUD_FUNCTION_URL", "http://localhost:8080")

test_cases = [
    "How AutoScout24 built a Bot Factory to standardize AI agent development with Amazon Bedrock",  # noqa: E501
    "What is PdM in EVs and why it entails monitoring, analyzing, and acting based on gathered insights", # noqa: E501
    "What do you recommend for studying for the AWS data engineering certification?",
]

for i, text in enumerate(test_cases, 1):
    print(f"\n{'=' * 80}")
    print(f"Test {i}: {text[:60]}...")
    print("=" * 80)

    response = requests.get(cloud_function_url, params={"phrase": text}, timeout=30)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
