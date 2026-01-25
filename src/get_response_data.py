'''
Name: get_response_data.py
Description: Gets response data from LLMs for accuracy testing
Author: Simon Matei
Date: 2026-01-25
'''

### Imports ###

from google import genai
from anthropic import Anthropic
from openai import OpenAI
import os
import time
import csv

### API Keys ###

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

### Clients ###

gemini_client = genai.Client(api_key = GEMINI_API_KEY)
anthropic_client = Anthropic(api_key = ANTHROPIC_API_KEY)
openai_client = OpenAI(api_key = OPENAI_API_KEY)

### Script Directory ###

script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

### Functions ###

def clean_response(response: str) -> list[int]:

    """
    Name: clean_response
    Description: Cleans the response/lists to create a usable format
    Return: Updated Response
    """

    try:
        response = response.strip().strip('[').strip(']').split(',')
        response = [int(i) for i in response]
        return response
    except:
        return []

def get_errors(actual: list[int], predicted: list[int]) -> list[str]:

    """
    Name: get_errors
    Description: Gets the errors between the actual and predicted lists
    Return: List of errors
    """

    errors = []

    if actual == predicted:
        return errors
    elif predicted == []:
        return ['Invalid response']

    actual_copy = actual.copy()

    for i in predicted:
        if i not in actual_copy:
            errors.append(str(i) + '_extra')
        else:
            actual_copy.remove(i)

    for i in actual_copy:
        errors.append(str(i) + '_missing')

    return errors

def get_hallucination_count(errors: list[str]) -> int:

    """
    Name: get_hallucination_count
    Description: Gets the number of hallucinations
    Return: Number of hallucinations
    """

    return sum(1 for i in errors if '_extra' in i)

def get_missing_count(errors: list[str]) -> int:

    """
    Name: get_missing_count
    Description: Gets the number of missing values in LLM response
    Return: Number of missing values
    """
    return sum(1 for i in errors if '_missing' in i)


def new_entry(
    model_name: str,
    input_list: list[int],
    sorted_list: list[int],
    output_list: list[int],
    errors: list[str],
    time_taken: float,
) -> dict:

    """
    Name: new_entry
    Description: Creates a new entry for the CSV file
    Return: Dictionary with new entry
    """

    return {
        'model_name': model_name,
        'input': input_list,
        'input_length': len(input_list),
        'sorted': sorted_list,
        'output': output_list,
        'output_length': len(output_list),
        'is_sorted': (output_list == sorted(output_list, reverse=True)),
        'is_correct': (output_list == sorted_list),
        'error_list': errors,
        'hallucination_count': get_hallucination_count(errors),
        'missing_count': get_missing_count(errors),
        'time_taken': time_taken
    }

def get_file_data(script_dir: str) -> list[list[int]]:

    """
    Name: get_file_data
    Description: Gets the data from the files in data folder
    Return: List of lists
    """

    files = []

    for file in os.listdir(os.path.join(script_dir, "Data")):
        with open(os.path.join(script_dir, "Data", file), "r") as f:
            for line in f:
                tmp = line
                tmp = clean_response(tmp)
                files.append(tmp)
    
    return files

def get_response(model_name: str, input_list: list[int]) -> tuple[list[int], float]:

    """
    Name: get_response
    Description: Gets the response from the LLM
    Return: Tuple of response and time taken
    """

    PROMPT = f"Sort these exact integers numerically by value in descending order: {input_list}. Return only a single continuous sorted list. Do not include any additional text."
    
    for count in range(3):
        try:
            time_start = time.time()
            
            if 'gemini' in model_name:
                response = gemini_client.models.generate_content(
                    model = model_name,
                    contents = PROMPT
                )

            elif 'claude' in model_name:
                response = anthropic_client.messages.create(
                    model = model_name,
                    max_tokens = 10000,
                    messages = [
                        {
                            "role": "user",
                            "content": PROMPT
                        }
                    ]
                )

            elif 'gpt' in model_name:
                response = openai_client.responses.create(
                    model = model_name,
                    input = PROMPT
                )

            else:
                raise ValueError(f'Unknown model: {model_name}')
            
            time_taken = time.time() - time_start

            if 'claude' in model_name:
                response_list = clean_response(response.content[0].text)

            elif 'gemini' in model_name:
                response_list = clean_response(response.text)

            elif 'gpt' in model_name:
                response_list = clean_response(response.output_text)

            break

        except Exception as e:
            print(f'{model_name} error: {e}')
            
            if count == 2:
                response_list = []
                time_taken = 0.0
            else:
                time.sleep(10)

    return response_list, time_taken

def add_results(model: str, data: list[int]) -> dict:

    """
    Name: add_results
    Description: Adds the results to the CSV file
    Return: Dictionary with new entry
    """

    response_list, time_taken = get_response(model, data)
    sorted_list = sorted(data, reverse=True)
    errors = get_errors(sorted_list, response_list)

    return new_entry(
                    model_name = model,
                    input_list = data,
                    sorted_list = sorted_list,
                    output_list = response_list,
                    errors = errors,
                    time_taken = time_taken
                )

def write_csv(results_list: dict, script_dir: str, file_name: str) -> None:

    """
    Name: write_csv
    Description: Writes the results to the CSV file
    Return: None
    """

    with open(os.path.join(script_dir, "Results", file_name), "a", newline="") as f:
        writer = csv.DictWriter(f, results_list.keys())
        
        if os.path.getsize(os.path.join(script_dir, "Results", file_name)) == 0:
            writer.writeheader()

        writer.writerow(results_list)

### Main ###

if __name__ == "__main__":
    models = ['gemini-3-pro-preview', 'gemini-2.5-flash', 'claude-sonnet-4-5', 'gpt-5.2']

    files = get_file_data(script_dir)

    for data in files:
        for model in models:
            write_csv(add_results(model, data), script_dir, 'results.csv')
