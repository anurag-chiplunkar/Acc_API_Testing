import requests
import pandas as pd
import json
import os

# --- Configuration ---
# IMPORTANT: Replace with your actual chatbot API URL
CHATBOT_API_URL = "http://your-chatbot-api-endpoint.com/query"

# Path to the text file containing user queries (one query per line)
INPUT_QUERIES_FILE = "user_queries.txt"

# Path for the output Excel file
OUTPUT_EXCEL_FILE = "chatbot_test_results.xlsx"

# --- Main Function ---
def test_chatbot():
    """
    Reads queries from a file, sends them to the chatbot API,
    and stores the results in an Excel file.
    """
    test_results = [] # List to store dictionaries for each row in Excel

    print(f"Starting chatbot testing process...")
    print(f"Reading queries from: {INPUT_QUERIES_FILE}")

    # Check if the input queries file exists
    if not os.path.exists(INPUT_QUERIES_FILE):
        print(f"Error: Input file '{INPUT_QUERIES_FILE}' not found.")
        print("Please create 'user_queries.txt' and add your natural language queries, one per line.")
        return

    try:
        with open(INPUT_QUERIES_FILE, 'r', encoding='utf-8') as f:
            user_queries = [line.strip() for line in f if line.strip()] # Read non-empty lines
        
        if not user_queries:
            print(f"No queries found in '{INPUT_QUERIES_FILE}'. Please add queries to the file.")
            return

        print(f"Found {len(user_queries)} queries to test.")

        for i, query in enumerate(user_queries):
            print(f"\n--- Processing Query {i+1}/{len(user_queries)}: '{query}' ---")
            
            # Prepare the payload for your chatbot API
            # IMPORTANT: Adjust this dictionary structure to match your chatbot's expected payload
            payload = {
                "gateway": "",
                "service_provider": "",
                "kb_connector": "",
                "catalog_provider": "",
                "model_params": {
                    "model_url": "",
                    "api_version": "",
                    "tuning_params": {
                        "model+: "",
                        "max_tokens": 0,
                        "top_p": 1.0,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "stop": "string"
                    }
                },
                "user_query": ""
                # Add any other required parameters here, e.g., "session_id": "test_session"
            }

            try:
                # Send the request to the chatbot API
                # You might need to adjust headers if your API requires them (e.g., API key)
                headers = {
                    "host_name": key,
                    "https_path": key,
                    "client_id": key,
                    "client_secret": key,
                    "Content-Type": "application/json"
                }
                response = requests.post(CHATBOT_API_URL, json=payload, headers=headers, timeout=30)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

                chatbot_response_data = response.json()

                # IMPORTANT: Adjust these keys to match the actual keys in your chatbot's response
                # For example, if your bot returns {"sql": "...", "data": "..."}, change these.
                generated_sql = chatbot_response_data.get("sql_query", "N/A")
                db_response = chatbot_response_data.get("db_response", "N/A")

                print(f"  Generated SQL: {generated_sql}")
                print(f"  DB Response (partial): {str(db_response)[:100]}{'...' if len(str(db_response)) > 100 else ''}")

                test_results.append({
                    "Original Query": query,
                    "Generated SQL": generated_sql,
                    "Database Response": str(db_response) # Convert response to string for Excel
                })

            except requests.exceptions.Timeout:
                print(f"  Error: Request timed out for query '{query}'")
                test_results.append({
                    "Original Query": query,
                    "Generated SQL": "Request Timeout",
                    "Database Response": "Request Timeout"
                })
            except requests.exceptions.RequestException as e:
                print(f"  Error sending request for query '{query}': {e}")
                print(f"  Response content: {response.text if 'response' in locals() else 'No response received'}")
                test_results.append({
                    "Original Query": query,
                    "Generated SQL": "API Error",
                    "Database Response": f"API Error: {e}"
                })
            except json.JSONDecodeError:
                print(f"  Error: Could not decode JSON response for query '{query}'")
                test_results.append({
                    "Original Query": query,
                    "Generated SQL": "Invalid JSON Response",
                    "Database Response": response.text if 'response' in locals() else "No response received"
                })
            except KeyError as e:
                print(f"  Error: Missing expected key in chatbot response for query '{query}': {e}")
                print(f"  Full response received: {chatbot_response_data}")
                test_results.append({
                    "Original Query": query,
                    "Generated SQL": "Response Key Error",
                    "Database Response": f"Missing key: {e}. Full response: {chatbot_response_data}"
                })


        # Create a Pandas DataFrame and save to Excel
        if test_results:
            df = pd.DataFrame(test_results)
            df.to_excel(OUTPUT_EXCEL_FILE, index=False)
            print(f"\n--- Testing Complete ---")
            print(f"Results saved to '{OUTPUT_EXCEL_FILE}' successfully.")
        else:
            print("\nNo test results to save.")

    except FileNotFoundError:
        print(f"Error: The file '{INPUT_QUERIES_FILE}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Call the main function to run the test
if __name__ == "__main__":
    test_chatbot()
