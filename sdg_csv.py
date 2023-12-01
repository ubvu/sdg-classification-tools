import pandas as pd
import requests
import json
import time
from datetime import datetime
import yaml
import os
import numpy as np  # Import numpy for percentile calculation
from tqdm import tqdm  # Import tqdm for the progress bar

# Global variable to control stopping
stop_classification = False

def set_stop_classification(value: bool):
    global stop_classification
    stop_classification = value

# Function to load config settings
def load_config():
    config_path = './config.yaml'  # Adjust this path as needed
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

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

def process_csv(file_path, output_path, sdg_threshold, classifier_url, input_base_name, rate_limit=None, update_progress=None):
    """
    Process the CSV file by classifying each row with the SDG classifier and appending the results.

    Args:
    file_path (str): Path to the input CSV file.
    output_path (str): Directory where the output CSV file will be saved.
    sdg_threshold (float): Threshold value for SDG predictions.
    classifier_url (str): URL of the SDG classifier API.
    input_base_name (str): Base name of the input file for naming the output file.
    """
    global stop_classification
    
    # Load config if rate_limit is not provided
    if rate_limit is None:
        config = load_config()
        rate_limit = float(config['rate_limit'])
    
    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # count total number of rows in the csv file
    total_rows = len(df)

    # Create a dynamic column name based on the configured SDG threshold
    sdg_column_name = f'SDG_{int(sdg_threshold * 100)}%_certainty'

    # Create a dynamic column name for the threshold-based percentile
    sdg_percentile_column_name = f'SDG_Top_{int(sdg_threshold * 100)}th_Percentile'

    # Initialize columns for each SDG and the dynamic threshold column
    for i in range(1, 18):
        df[f'SDG_{i}'] = 0.0
    df[sdg_column_name] = ''
    df['SDG_AVG'] = 0.0  # New column for average SDG score
    df['SDG_90th_percentile'] = 0.0  # New column for 90th percentile SDG score
    df['SDG_Top_3'] = '' # Initialize a new column for Top 3 SDGs
    df['SDG_Top_AVG'] = ''  # New column for SDGs above average
    df['SDG_Top_90th_percentile'] = ''  # New column for SDGs above 90th percentile
    df[sdg_percentile_column_name] = 0.0 # New column for SDGs above the treshol value as percentile
    df['Classifier_Model_Used'] = classifier_url  # Use the classifier url from config

    # Determine whether to use tqdm or update_progress based on if update_progress is provided
    iterator = tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows") if update_progress is None else df.iterrows()

    for index, row in iterator:
        if stop_classification:
            print("Stopping classification...")
            break
        
        # Skip processing if the 'Abstract' field is blank
        if pd.isna(row['Abstract']) or row['Abstract'].strip() == '':
            continue

        # Update progress for GUI if update_progress function is provided
        if update_progress is not None:
            current_progress = (index + 1) / total_rows * 100
            update_progress(current_progress, total_rows, rate_limit)

        # Apply a rate limit to respect API constraints
        time.sleep(rate_limit) 

        # Retrieve SDG predictions for the text
        sdg_predictions = classify_text_sdg(row['Abstract'], classifier_url)
        if not sdg_predictions:
            continue

        # Sort predictions by score and get top 3 SDGs with their percentages
        top_3_sdg = sorted(sdg_predictions, key=lambda x: x['prediction'], reverse=True)[:3]
        
        # Format the "SDG_Top_3" column to include the SDG code (padded with zeros to two digits), the prediction score (converted to a percentage and rounded to no decimal places), and the SDG name. This formatting provides a clear and detailed overview of the top SDG predictions for each row.
        top_3_sdg_formatted = [f"SDG {str(sdg['sdg']['code']).zfill(2)} ({sdg['prediction']*100:.0f}%) {sdg['sdg']['name']}" for sdg in top_3_sdg]
        
        # Update the DataFrame with the top 3 SDGs
        df.at[index, 'SDG_Top_3'] = ' | '.join(top_3_sdg_formatted)

        # Calculating average and 90th percentile scores
        scores = [pred['prediction'] for pred in sdg_predictions]
        average_score = np.mean(scores)
        percentile_90_score = np.percentile(scores, 90)
        threshold_percentile_score = np.percentile(scores, sdg_threshold * 100)  # Calculate the percentile based on the threshold
        
        df.at[index, 'SDG_AVG'] = average_score
        df.at[index, 'SDG_90th_percentile'] = percentile_90_score
        df.at[index, sdg_percentile_column_name] = threshold_percentile_score
          
        # Filtering SDGs above average, the 90th percentile, and the threshold percentile.
        sdg_above_avg = [pred for pred in sdg_predictions if pred['prediction'] >= average_score]
        sdg_above_90th = [pred for pred in sdg_predictions if pred['prediction'] >= percentile_90_score]
        sdg_above_threshold = [pred for pred in sdg_predictions if pred['prediction'] >= threshold_percentile_score]

        # Formatting SDGs for the new columns
        df.at[index, 'SDG_Top_AVG'] = ' | '.join([f"SDG {str(sdg['sdg']['code']).zfill(2)} ({sdg['prediction']*100:.0f}%) {sdg['sdg']['name']}" for sdg in sdg_above_avg])
        df.at[index, 'SDG_Top_90th_percentile'] = ' | '.join([f"SDG {str(sdg['sdg']['code']).zfill(2)} ({sdg['prediction']*100:.0f}%) {sdg['sdg']['name']}" for sdg in sdg_above_90th])
        df.at[index, sdg_percentile_column_name] = ' | '.join([f"SDG {str(sdg['sdg']['code']).zfill(2)} ({sdg['prediction']*100:.0f}%) {sdg['sdg']['name']}" for sdg in sdg_above_threshold])

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
    print("Progress saved to:", new_file_path)

def main():
    """
    Main function to run the script. It reads configuration settings, prepares file paths,
    and initiates the CSV processing.
    """
    
    # Read the configuration settings from the YAML file
    config = load_config()

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
