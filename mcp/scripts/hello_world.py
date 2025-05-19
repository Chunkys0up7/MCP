"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
"""

import requests
import sys
from datetime import datetime

def main():
    try:
        # Use the input variables
        name = name if 'name' in globals() else "World"
        language = language if 'language' in globals() else "en"
        
        # Get current time
        current_time = datetime.now().strftime("%H:%M:%S")
        
        # Print a greeting
        greeting = f"Hello, {name}! The current time is {current_time}"
        print(greeting)
        
        # Try to get a random fact (demonstrates using requirements)
        try:
            response = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random")
            response.raise_for_status()
            fact = response.json()["text"]
            print(f"\nRandom fact: {fact}")
        except requests.exceptions.RequestException as e:
            print(f"\nCouldn't fetch a random fact: {str(e)}")
        
        # Return success
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 