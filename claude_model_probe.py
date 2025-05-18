import os
import requests

api_key = "REMOVED_CLAUDE_API_KEY "

headers = {
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}

# Test a simple message to verify connectivity
data = {
    "model": "claude-3-opus-20240229",
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Hello, this is a test message."
        }
    ]
}

response = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers=headers,
    json=data
)

print("Status code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response text:", response.text) 