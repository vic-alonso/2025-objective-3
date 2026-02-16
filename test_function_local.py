import sys
sys.path.insert(0, 'cloud-function')

import numpy as np
from main import recommend_article
from unittest.mock import Mock

test_cases = [
    "How AutoScout24 built a Bot Factory to standardize AI agent development with Amazon Bedrock",
    "What is PdM in EVs and why it entails monitoring, analyzing, and acting based on gathered insights",
    "What do you recommend for studying for the AWS data engineering certification?"
]

for i, text in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}: {text[:60]}...")
    print('='*80)
    
    request = Mock()
    request.args.get = lambda key: text if key == "phrase" else None
    
    result, status = recommend_article(request)
    
    print(f"Status: {status}")
    print(f"Response: {result}")
