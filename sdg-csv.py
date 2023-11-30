import pandas as pd
import requests
import json
import time
from datetime import datetime
import yaml
import os

def classify_text_sdg(text, classifier_url):
    """
    Classify the given text using the SDG classifier API.

    Args:
    text (str): Text to be classified.
    classifier_url (str): URL of the SDG classifier API.

    Returns:
    dict: Predictions from the SDG classifier.
    """
    
    # Convert the text to JSON format and set the appropriate headers
    payload = json.dumps({"text": text})
    headers = {'Content-Type': 'application/json'}

    # Make a POST request to the classifier API and return the predictions
    response = requests.request("POST", classifier_url, headers=headers, data=payload, verify=False)
    if response.status_code == 200:
        return response.json()['predictions']
    else:
        return None

def process_csv(file_path, output_path, sdg_threshold, classifier_url, input_base_name):
    """
    Process the CSV file by classifying each row with the SDG classifier and appending the results.

    Args:
    file_path (str): Path to the input CSV file.
    output_path (str): Directory where the output CSV file will be saved.
    sdg_threshold (float): Threshold value for SDG predictions.
    classifier_url (str): URL of the SDG classifier API.
    input_base_name (str): Base name of the input file for naming the output file.
    """
    
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Create a dynamic column name based on the configured SDG threshold
    sdg_column_name = f'SDG_{int(sdg_threshold * 100)}%_certainty'

    # Initialize columns for each SDG and the dynamic threshold column
    for i in range(1, 18):
        df[f'SDG_{i}'] = 0.0
    df[sdg_column_name] = ''
    df['Classifier_Model_Used'] = classifier_url  # Use the classifier url from config

    for index, row in df.iterrows():
        # Skip processing if the 'Abstract' field is blank
        if pd.isna(row['Abstract']) or row['Abstract'].strip() == '':
            continue

        # Apply a rate limit to respect API constraints
        time.sleep(0.2) 

        # Retrieve SDG predictions for the text
        sdg_predictions = classify_text_sdg(row['Abstract'], classifier_url)
        if not sdg_predictions:
            continue

        # Collect SDGs that meet the threshold criteria
        sdg_list = []
        for prediction in sdg_predictions:
            sdg_code = int(prediction['sdg']['code'])
            sdg_name = prediction['sdg']['name']
            prediction_value = prediction['prediction']
            df.at[index, f'SDG_{sdg_code}'] = prediction_value
            if prediction_value >= sdg_threshold:
                sdg_list.append(sdg_name)

        # Update the DataFrame with the collected SDGs
        df.at[index, sdg_column_name] = '|'.join(sdg_list)

    # Generate a timestamped output file name
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_file_name = f'{input_base_name}_sdg_{current_datetime}.csv'
    new_file_path = os.path.join(output_path, new_file_name)

    # Save the processed DataFrame to a CSV file
    df.to_csv(new_file_path, index=False)

def main():
    """
    Main function to run the script. It reads configuration settings, prepares file paths,
    and initiates the CSV processing.
    """
    
    # Read the configuration settings from the YAML file
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    # Construct the full paths for input and output
    input_file = config['data_input_file']
    input_path = os.path.join(config['data_input_folder'], input_file)
    output_path = config['data_output_folder']
    sdg_threshold = config['sdg_threshold']
    classifier_url = config['classifier_url']

    # Extract the base name of the input file for use in the output file name
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Process the CSV file
    process_csv(input_path, output_path, sdg_threshold, classifier_url, input_base_name)

if __name__ == "__main__":
    main()
