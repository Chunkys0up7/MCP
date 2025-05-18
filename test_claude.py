import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# Test API connection
headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

data = {
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Hello, this is a test message."
        }
    ]
}

try:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    
    print("Status code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", str(e)) 