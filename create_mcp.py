import requests

mcp_data = {
    "name": "Hello World Example",
    "description": "A simple hello world example that demonstrates input variables and requirements",
    "type": "python_script",
    "config": {
        "type": "python_script",
        "name": "Hello World Example",
        "script_path": "mcp/scripts/hello_world.py",
        "requirements": ["requests==2.31.0"],
        "input_variables": ["name", "language"],
        "virtual_env": True,
        "timeout": 600
    }
}

response = requests.post(
    "http://localhost:8000/mcps",
    json=mcp_data
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}") 