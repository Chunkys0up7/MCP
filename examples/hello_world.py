"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
"""

import requests
import sys

def main():
    try:
        # Use the input variables
        name = "World"  # Initialize with a default value
        language = "en"  # Initialize with a default value
        
        # Make a request to a greeting API
        response = requests.get(f"https://api.greeting.com/greet?name={name}&lang={language}")
        response.raise_for_status()
        
        # Print the greeting
        print(response.json()["greeting"])
        
        # Return success
        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to get greeting - {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 