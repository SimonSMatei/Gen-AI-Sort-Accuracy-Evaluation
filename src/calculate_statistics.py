'''
Name: calculate_statistics.py
Description: Generates statistics from the response data
Author: Simon Matei
Date: 2026-01-25
'''

import pandas as pd
import json
import os

def clean_response(response: str) -> list[int]:
    try:
        response = response.strip().strip('[').strip(']').split(',')
        response = [int(i) for i in response]
        return response
    except:
        return []

def seperate_data(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    max_vals = data['input'].apply(lambda x: max(clean_response(x)))

    trial_10 = data[data['input_length'] == 10]

    trial_500 = data[data['input_length'] == 500]

    trial_100 = data[(data['input_length'] == 100) & (max_vals > 10)]

    trial_duplicates = data[(data['input_length'] == 100) & (max_vals <= 10)]

    return trial_10, trial_100, trial_500, trial_duplicates

def get_benchmark(trial_10: pd.DataFrame, trial_100: pd.DataFrame, trial_500: pd.DataFrame, trial_duplicates: pd.DataFrame) -> dict:
    models = trial_10['model_name'].unique()

    benchmark = {}

    for model in models:

        model_trial_10 = trial_10[trial_10['model_name'] == model]
        model_trial_100 = trial_100[trial_100['model_name'] == model]
        model_trial_500 = trial_500[trial_500['model_name'] == model]
        model_trial_duplicates = trial_duplicates[trial_duplicates['model_name'] == model]

        model_trial_10_failed = model_trial_10[model_trial_10['is_correct'] == False]
        model_trial_100_failed = model_trial_100[model_trial_100['is_correct'] == False]
        model_trial_500_failed = model_trial_500[model_trial_500['is_correct'] == False]
        model_trial_duplicates_failed = model_trial_duplicates[model_trial_duplicates['is_correct'] == False]

        benchmark[model] = {
            'trial_10': {
                'accuracy (%)': get_accuracy(model_trial_10) * 100,
                'latency (s)': get_average_latency(model_trial_10),
                'latency_std (s)': get_latency_std(model_trial_10),
                'hallucination_rate (%)': get_hallucination_rate(model_trial_10_failed) * 100,
                'missing_rate (%)': get_missing_rate(model_trial_10_failed) * 100,
                'sorting_error_rate (%)': get_sorting_error_rate(model_trial_10_failed) * 100,
                'format_error_rate (%)': get_format_error_rate(model_trial_10_failed) * 100,
                'hallucination_and_missing_rate (%)': get_hallucination_and_missing_rate(model_trial_10_failed) * 100,
                'pure_hallucination_rate (%)': get_pure_hallucination_rate(model_trial_10_failed) * 100,
                'pure_missing_rate (%)': get_pure_missing_rate(model_trial_10_failed) * 100,
                'pure_sorting_error_rate (%)': get_pure_sorting_error_rate(model_trial_10_failed) * 100
            },
            'trial_100': {
                'accuracy (%)': get_accuracy(model_trial_100) * 100,
                'latency (s)': get_average_latency(model_trial_100),
                'latency_std (s)': get_latency_std(model_trial_100),
                'hallucination_rate (%)': get_hallucination_rate(model_trial_100_failed) * 100,
                'missing_rate (%)': get_missing_rate(model_trial_100_failed) * 100,
                'sorting_error_rate (%)': get_sorting_error_rate(model_trial_100_failed) * 100,
                'format_error_rate (%)': get_format_error_rate(model_trial_100_failed) * 100,
                'hallucination_and_missing_rate (%)': get_hallucination_and_missing_rate(model_trial_100_failed) * 100,
                'pure_hallucination_rate (%)': get_pure_hallucination_rate(model_trial_100_failed) * 100,
                'pure_missing_rate (%)': get_pure_missing_rate(model_trial_100_failed) * 100,
                'pure_sorting_error_rate (%)': get_pure_sorting_error_rate(model_trial_100_failed) * 100
            },
            'trial_500': {
                'accuracy (%)': get_accuracy(model_trial_500) * 100,
                'latency (s)': get_average_latency(model_trial_500),
                'latency_std (s)': get_latency_std(model_trial_500),
                'hallucination_rate (%)': get_hallucination_rate(model_trial_500_failed) * 100,
                'missing_rate (%)': get_missing_rate(model_trial_500_failed) * 100,
                'sorting_error_rate (%)': get_sorting_error_rate(model_trial_500_failed) * 100,
                'format_error_rate (%)': get_format_error_rate(model_trial_500_failed) * 100,
                'hallucination_and_missing_rate (%)': get_hallucination_and_missing_rate(model_trial_500_failed) * 100,
                'pure_hallucination_rate (%)': get_pure_hallucination_rate(model_trial_500_failed) * 100,
                'pure_missing_rate (%)': get_pure_missing_rate(model_trial_500_failed) * 100,
                'pure_sorting_error_rate (%)': get_pure_sorting_error_rate(model_trial_500_failed) * 100
            },
            'trial_duplicates': {
                'accuracy (%)': get_accuracy(model_trial_duplicates) * 100,
                'latency (s)': get_average_latency(model_trial_duplicates),
                'latency_std (s)': get_latency_std(model_trial_duplicates),
                'hallucination_rate (%)': get_hallucination_rate(model_trial_duplicates_failed) * 100,
                'missing_rate (%)': get_missing_rate(model_trial_duplicates_failed) * 100,
                'sorting_error_rate (%)': get_sorting_error_rate(model_trial_duplicates_failed) * 100,
                'format_error_rate (%)': get_format_error_rate(model_trial_duplicates_failed) * 100,
                'hallucination_and_missing_rate (%)': get_hallucination_and_missing_rate(model_trial_duplicates_failed) * 100,
                'pure_hallucination_rate (%)': get_pure_hallucination_rate(model_trial_duplicates_failed) * 100,
                'pure_missing_rate (%)': get_pure_missing_rate(model_trial_duplicates_failed) * 100,
                'pure_sorting_error_rate (%)': get_pure_sorting_error_rate(model_trial_duplicates_failed) * 100
            }
        }
    
    return benchmark

def get_accuracy(data: pd.DataFrame) -> float:
    return (data['is_correct'] == True).sum() / len(data)

def get_average_latency(data: pd.DataFrame) -> float:
    return data['time_taken'].mean()

def get_latency_std(data: pd.DataFrame) -> float:
    return data['time_taken'].std()
    
def get_hallucination_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    hallucinations = data[data['hallucination_count'] > 0]

    return len(hallucinations) / len(data)

def get_missing_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    missing = data[data['missing_count'] > 0]

    return len(missing) / len(data)
    
def get_sorting_error_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    sorting_errors = data[data['is_sorted'] == False]

    return len(sorting_errors) / len(data)

def get_format_error_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    format_errors = data[data['error_list'] == "['Invalid response']"]

    return len(format_errors) / len(data)

def get_hallucination_and_missing_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    hallucinations_and_missing = data[(data['hallucination_count'] > 0) & (data['missing_count'] > 0)]

    return len(hallucinations_and_missing) / len(data)

def get_pure_hallucination_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    pure_hallucinations = data[(data['hallucination_count'] > 0) & (data['missing_count'] == 0)]

    return len(pure_hallucinations) / len(data)

def get_pure_missing_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    pure_missing = data[(data['missing_count'] > 0) & (data['hallucination_count'] == 0)]

    return len(pure_missing) / len(data)

def get_pure_sorting_error_rate(data: pd.DataFrame) -> float:
    if len(data) == 0:
        return 0

    pure_sorting_errors = data[(data['is_sorted'] == False) & (data['hallucination_count'] == 0) & (data['missing_count'] == 0)]

    return len(pure_sorting_errors) / len(data)

script_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Results")

if __name__ == "__main__":
    data = pd.read_csv(os.path.join(script_dir, "results.csv"))
    
    trial_10, trial_100, trial_500, trial_duplicates = seperate_data(data)

    benchmark = get_benchmark(trial_10, trial_100, trial_500, trial_duplicates)

    with open(os.path.join(script_dir, "response_benchmark.json"), "w") as f:
        json.dump(benchmark, f, indent=4)
    
