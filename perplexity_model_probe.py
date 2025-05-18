import os
import requests

api_key = os.getenv("PERPLEXITY_API_KEY")
if not api_key:
    raise Exception("Set PERPLEXITY_API_KEY in your environment.")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": "invalid-model-name",
    "messages": [
        {"role": "user", "content": "Hello, what models do you support?"}
    ]
}

response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    headers=headers,
    json=data
)

print("Status code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception:
    print("Response text:", response.text) 