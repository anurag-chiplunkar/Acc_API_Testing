import requests
import pandas as pd
import json
import os
from datetime import datetime

CHATBOT_API_URL = "http://your-chatbot-api-endpoint.com/query"

INPUT_QUERIES_FILE = "user_queries.txt"

OUTPUT_EXCEL_FILENAME_BASE = "chatbot_test_results"

def test_chatbot():
    """
    Reads queries from a file, sends them to the chatbot API,
    and stores the results in an Excel file. The output file name
    is validated against the current date for appending or creating a new file.
    """
    test_results = []

    print(f"Starting chatbot testing process...")
    print(f"Reading queries from: {INPUT_QUERIES_FILE}")

    current_date = datetime.now().strftime("%Y-%m-%d")
    OUTPUT_EXCEL_FILE = f"{OUTPUT_EXCEL_FILENAME_BASE}_{current_date}.xlsx"

    if not os.path.exists(INPUT_QUERIES_FILE):
        print(f"Error: Input file '{INPUT_QUERIES_FILE}' not found.")
        print("Please create 'user_queries.txt' and add your natural language queries, one per line.")
        return

    try:
        with open(INPUT_QUERIES_FILE, 'r', encoding='utf-8') as f:
            user_queries = [line.strip() for line in f if line.strip()] 
        
        if not user_queries:
            print(f"No queries found in '{INPUT_QUERIES_FILE}'. Please add queries to the file.")
            return

        print(f"Found {len(user_queries)} queries to test.")

        for i, query in enumerate(user_queries):
            print(f"\n--- Processing Query {i+1}/{len(user_queries)}: '{query}' ---")
            
            payload = {
                "gateway": "",
                "service_provider": "",
                "kb_connector": "",
                "catalog_provider": "",
                "model_params": {
                    "model_url": "",
                    "api_version": "",
                    "tuning_params": {
                        "model": "",
                        "max_tokens": 0,
                        "top_p": 1.0,
                        "frequency_penalty": 0,
                        "presence_penalty": 0,
                        "stop": "string"
                    }
                },
                "user_query": query 
            }

            try:
                headers = {
                    "host_name": "your_host_name",    
                    "https_path": "your_https_path",  
                    "client_id": "your_client_id",   
                    "client_secret": "your_client_secret", 
                    "Content-Type": "application/json"
                }
                response = requests.post(CHATBOT_API_URL, json=payload, headers=headers, timeout=30)
                response.raise_for_status() 

                chatbot_response_data = response.json()

                generated_sql = chatbot_response_data.get("sql_query", "N/A")
                db_response = chatbot_response_data.get("db_response", "N/A")

                print(f"  Generated SQL: {generated_sql}")
                print(f"  DB Response (partial): {str(db_response)[:100]}{'...' if len(str(db_response)) > 100 else ''}")

                test_results.append({
                    "Original Query": query,
                    "Generated SQL": generated_sql,
                    "Database Response": str(db_response)
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


        new_df = pd.DataFrame(test_results)

        if os.path.exists(OUTPUT_EXCEL_FILE):
            print(f"\nAppending results to existing file: '{OUTPUT_EXCEL_FILE}'")
            try:
                existing_df = pd.read_excel(OUTPUT_EXCEL_FILE)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception as e:
                print(f"Error reading existing Excel file, creating new one: {e}")
                combined_df = new_df 
        else:
            print(f"\nCreating new file for today: '{OUTPUT_EXCEL_FILE}'")
            combined_df = new_df
        
        if not combined_df.empty:
            combined_df.to_excel(OUTPUT_EXCEL_FILE, index=False)
            print(f"--- Testing Complete ---")
            print(f"Results saved to '{OUTPUT_EXCEL_FILE}' successfully.")
        else:
            print("\nNo test results to save.")

    except FileNotFoundError:
        print(f"Error: The file '{INPUT_QUERIES_FILE}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_chatbot()
