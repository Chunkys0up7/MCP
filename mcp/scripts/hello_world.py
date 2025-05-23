"""
A simple hello world example that demonstrates:
1. Using input variables
2. Using external packages (requests)
3. Basic error handling
4. Unicode character support
"""

import sys
import json
from datetime import datetime

# Set default encoding to UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main(name: str, language: str) -> dict:
    """Generate a hello world message in the specified language.
    
    Args:
        name (str): The name to greet
        language (str): The language to use for the greeting
        
    Returns:
        dict: The greeting message and metadata
    """
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!",
        "de": f"Hallo, {name}!",
        "it": f"Ciao, {name}!",
        "pt": f"Olá, {name}!",
        "ru": f"Привет, {name}!",
        "zh": f"你好，{name}！",
        "ja": f"こんにちは、{name}さん！",
        "ko": f"안녕하세요, {name}님!"
    }
    
    # Default to English if language not found
    greeting = greetings.get(language.lower(), f"Hello, {name}!")
    
    # Return a dictionary with the greeting and metadata
    return {
        "greeting": greeting,
        "language": language,
        "name": name,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Get command line arguments
    if len(sys.argv) != 3:
        print(json.dumps({
            "error": "Usage: python hello_world.py <name> <language>"
        }, ensure_ascii=False))
        sys.exit(1)
        
    name = sys.argv[1]
    language = sys.argv[2]
    
    try:
        result = main(name, language)
        # Ensure we're using UTF-8 for JSON output and handle any encoding issues
        try:
            print(json.dumps(result, ensure_ascii=False))
        except UnicodeEncodeError:
            # Fallback to ASCII with escaped Unicode if UTF-8 fails
            print(json.dumps(result, ensure_ascii=True))
    except Exception as e:
        print(json.dumps({
            "error": str(e)
        }, ensure_ascii=False))
        sys.exit(1) 