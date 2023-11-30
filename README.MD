# SDG Classification

## Description
The `sdg-classification` script is designed to process CSV files containing text data, specifically in the 'Abstract' column, and classify each entry using the Sustainable Development Goals (SDG) classifier API. The script allows for configuration of various parameters such as the classifier model, SDG threshold, and input/output file paths, making it versatile for different datasets and use cases.

## TL;DR
The script reads text data from a CSV file, classifies it using the SDG classifier API, and appends the results to the file, exporting it with a new name indicating the process completion date and time.

## Prerequisites
Before you begin, ensure you have met the following requirements:
- Python 3.x installed on your system
- Access to command-line/terminal
- Internet connection for API access and package installation

## Installation
To install `sdg-classification`, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/ubvu/sdg-classification.git
    cd sdg-classification
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv env
    ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     env\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source env/bin/activate
     ```

4. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration
Configure the script by editing the `config.yaml` file. Set the following parameters:
- `data_input_folder`: Directory containing the input CSV file.
- `data_input_file`: Name of the input CSV file.
- `data_output_folder`: Directory where the output file will be saved.
- `sdg_threshold`: Threshold for SDG classification.
- `classifier_url`: URL of the SDG classifier API. Use `"https://aurora-sdg.labs.vu.nl/classifier/classify/aurora-sdg-multi"` for the fast model or `"https://aurora-sdg.labs.vu.nl/classifier/classify/aurora-sdg"` for the slower, more accurate model.

Example `config.yaml`:
```yaml
data_input_folder: /path/to/input/
data_input_file: input.csv
data_output_folder: /path/to/output/
sdg_threshold: 0.98
classifier_url: "https://aurora-sdg.labs.vu.nl/classifier/classify/aurora-sdg-multi"
```

## Running the Script
To run `sdg-classification`, execute the following command in your terminal:

```bash
python sdg-csv.py
```

The script will process the specified CSV file and generate the output in the configured directory.

---

Feel free to contribute to the development of this project by submitting pull requests or opening issues for any bugs or feature requests.