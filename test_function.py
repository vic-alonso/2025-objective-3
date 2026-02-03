import sys
sys.path.insert(0, 'cloud-function')

from main import recommend_article
from unittest.mock import Mock

request = Mock()
request.args.get = lambda key: "How AutoScout24 built a Bot Factory to standarize AI agent development with Amazon Bedrock"

print("Testing recommend_article function...")
result = recommend_article(request)
print("\nResult:")
print(result)
