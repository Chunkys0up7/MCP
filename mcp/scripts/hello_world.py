"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
"""

import requests
import sys
import json
from datetime import datetime

def main():
    try:
        # Get input variables with defaults
        name = globals().get('name', "World")
        language = globals().get('language', "en")
        
        # Get current time
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Create greeting
        greeting = f"Hello, {name}! The current time is {current_time}"
        print(greeting)
        
        # Try to get a random fact (demonstrates using requirements)
        fact = None
        try:
            response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
            response.raise_for_status()
            fact = response.json()["text"]
            print(f"\nRandom fact: {fact}")
        except requests.exceptions.RequestException as e:
            print(f"\nCouldn't fetch a random fact: {str(e)}")
        
        # Return results as dictionary
        result = {
            "status": "success",
            "greeting": greeting,
            "fact": fact,
            "timestamp": current_time
        }
        print(json.dumps(result))  # Print the result as JSON
        return result
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg, file=sys.stderr)
        result = {
            "status": "error",
            "error": error_msg
        }
        print(json.dumps(result))  # Print the error as JSON
        return result

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result["status"] == "success" else 1) 