# tests/workflow_mcp_scripts.py
"""
This file stores the Python script content for MCPs used in workflow tests.
These scripts are designed to be used when creating PythonScriptMCP instances via the API for testing purposes.
Each script reads input from a JSON file (path in sys.argv[1]) and writes output to another JSON file (path in sys.argv[2]).
The output JSON should be a dictionary: {"success": bool, "result": Dict|None, "error": str|None}.
"""

ECHO_MCP_SCRIPT = """
import json
import sys

def execute_mcp(inputs: dict) -> dict:
    input_string = inputs.get("input_string")
    if input_string is None:
        return {"success": False, "result": None, "error": "Missing 'input_string' in inputs"}
    return {"success": True, "result": {"output_string": input_string}, "error": None}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_json_path> <output_json_path>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            incoming_inputs = json.load(f_in)
    except Exception as e:
        # Write error directly to output file if input loading fails
        error_output = {"success": False, "result": None, "error": f"Failed to read or parse input JSON: {str(e)}"}
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            json.dump(error_output, f_out, indent=2)
        sys.exit(1) # Indicate script error
        
    result_dict = execute_mcp(incoming_inputs)
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            json.dump(result_dict, f_out, indent=2)
    except Exception as e:
        # If writing the actual result fails, this is a critical script/system error.
        # We can't write to the output file anymore. Best to print to stderr.
        # The MCP framework will catch the non-zero exit code if we exit(1).
        print(f"Critical error: Failed to write output JSON to {output_file_path}: {str(e)}", file=sys.stderr)
        sys.exit(1)
"""

CONCAT_MCP_SCRIPT = """
import json
import sys

def execute_mcp(inputs: dict) -> dict:
    string1 = inputs.get("string1")
    string2 = inputs.get("string2")

    if string1 is None or string2 is None:
        missing = []
        if string1 is None: missing.append("string1")
        if string2 is None: missing.append("string2")
        return {"success": False, "result": None, "error": f"Missing required inputs: {', '.join(missing)}"}

    concatenated = str(string1) + str(string2)
    return {"success": True, "result": {"concatenated_string": concatenated}, "error": None}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_json_path> <output_json_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f_in:
            incoming_inputs = json.load(f_in)
    except Exception as e:
        error_output = {"success": False, "result": None, "error": f"Failed to read or parse input JSON: {str(e)}"}
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            json.dump(error_output, f_out, indent=2)
        sys.exit(1)
        
    result_dict = execute_mcp(incoming_inputs)
    
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f_out:
            json.dump(result_dict, f_out, indent=2)
    except Exception as e:
        print(f"Critical error: Failed to write output JSON to {output_file_path}: {str(e)}", file=sys.stderr)
        sys.exit(1)
""" 