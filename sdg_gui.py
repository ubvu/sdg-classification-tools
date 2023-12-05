import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yaml
import threading
import os  # Import the os module
import pandas as pd  # Import pandas to read the CSV file for record count
import sdg_csv  # Assuming sdg_csv.py is the module name of your script
from pandasgui import show

# Global variable to keep track of the classification state
is_classifying = False

# Function to load config settings
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Function to read column headers from the CSV file
def get_csv_columns(file_path):
    try:
        df = pd.read_csv(file_path)
        return df.columns.tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read file: {e}")
        return []

# Function to update the dropdown menu with column headers
def update_column_dropdown():
    file_path = file_input.get()
    columns = get_csv_columns(file_path)
    column_dropdown['values'] = columns
    if columns:
        column_dropdown.set(config['text_column'])  # Set default value from config

# Function to stop the classification and save progress
def stop_and_save():
    sdg_csv.set_stop_classification(True)

# Function to provide a live update to the progress bar as each row is processed. 
def update_progress(current_progress, total_rows, rate_limit):
    remaining = total_rows - int((current_progress / 100) * total_rows)
    estimated_time = remaining * rate_limit  # Calculate estimated time remaining
    progress_label.config(text=f"Records remaining: {remaining}, Estimated time: {estimated_time:.2f} seconds")
    progress_bar['value'] = current_progress
    root.update_idletasks()

# Function to start the classification process
def start_classification(input_file, output_folder, model_url, threshold, rate_limit, selected_column):
    global is_classifying
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    sdg_csv.process_csv(input_file, output_folder, threshold, model_url, input_base_name, selected_column, rate_limit, update_progress)
    is_classifying = False
    stop_button['state'] = 'disabled'  # Disable "Stop and Save" button
    messagebox.showinfo("Complete", "Classification completed successfully.")

# Function to handle the classification process in a separate thread
def classify():
    global is_classifying
    if is_classifying:
        messagebox.showwarning("Already Running", "Classification is already in progress.")
        return

    input_file = file_input.get()
    output_folder = folder_output.get()
    model_url = model_var.get()
    threshold = float(threshold_var.get())
    rate_limit = float(config['rate_limit'])  # Get rate limit from config
    progress_bar['value'] = 0

    # Enable "Stop and Save" button and start classification
    stop_button['state'] = 'normal'
    is_classifying = True

    # Start the classification process in a separate thread
    selected_column = column_dropdown.get()
    threading.Thread(target=start_classification, args=(input_file, output_folder, model_url, threshold, rate_limit, selected_column)).start()

# Function to open PandasGUI with the DataFrame
def open_pandasgui():
    # Load data into a DataFrame
    df = pd.read_csv('path_to_your_output_file.csv')
    # Open PandasGUI in a new thread to avoid blocking the Tkinter GUI
    threading.Thread(target=lambda: show(df)).start()


def stop_and_save():
    global is_classifying
    if is_classifying:
        sdg_csv.set_stop_classification(True)
        is_classifying = False
        stop_button['state'] = 'disabled'  # Disable "Stop and Save" button

# Load config
config = load_config()

# Create the main window
root = tk.Tk()
root.title("SDG Classification Tool")

# Input file selection
file_input = tk.StringVar(value=config['data_input_folder'] + config['data_input_file'])
file_input_entry = tk.Entry(root, textvariable=file_input, width=50)
file_input_entry.grid(row=0, column=1)
file_input_browse_button = tk.Button(root, text="Browse...", command=lambda: [file_input.set(filedialog.askopenfilename()), update_column_dropdown()])
file_input_browse_button.grid(row=0, column=2)

# Dropdown menu for selecting the text column
tk.Label(root, text="Select Text Column:").grid(row=1, column=0, sticky='w')
column_dropdown = ttk.Combobox(root, state="readonly")
column_dropdown.grid(row=1, column=1, sticky='w')

# Output folder selection
tk.Label(root, text="Select Output Folder:").grid(row=1, column=0, sticky='w')
folder_output = tk.StringVar(value=config['data_output_folder'])
tk.Entry(root, textvariable=folder_output, width=50).grid(row=1, column=1)
tk.Button(root, text="Browse...", command=lambda: folder_output.set(filedialog.askdirectory())).grid(row=1, column=2)

# Model selection
model_var = tk.StringVar(value=config['classifier_url'])
tk.Label(root, text="Select Model:").grid(row=2, column=0, sticky='w')
tk.Radiobutton(root, text="Fast Model (aurora-sdg-multi)", variable=model_var, value="https://aurora-sdg.labs.vu.nl/classifier/classify/aurora-sdg-multi").grid(row=2, column=1, sticky='w')
tk.Radiobutton(root, text="Slow Model (aurora-sdg)", variable=model_var, value="https://aurora-sdg.labs.vu.nl/classifier/classify/aurora-sdg").grid(row=2, column=2, sticky='w')

# Threshold selection
threshold_var = tk.StringVar(value=str(config['sdg_threshold']))
tk.Label(root, text="Certainty Threshold:").grid(row=3, column=0, sticky='w')
tk.Entry(root, textvariable=threshold_var, width=10).grid(row=3, column=1, sticky='w')

# "Classify" button
tk.Button(root, text="Classify", command=classify).grid(row=4, column=1)

# "Stop and Save" button (initially disabled)
stop_button = tk.Button(root, text="Stop and Save", command=stop_and_save, state='disabled')
stop_button.grid(row=4, column=2)

# Progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=6, column=0, columnspan=3, pady=10)

# Progress label for records remaining and estimated time
progress_label = tk.Label(root, text="Records remaining: 0, Estimated time: 0 seconds")
progress_label.grid(row=7, column=0, columnspan=3)


# Tool Description
description_text = """SDG Classification Tool:
This tool processes CSV files containing text data and classifies each entry using the Sustainable Development Goals (SDG) classifier API. 
You can configure the input/output paths, select the classification model, and set a certainty threshold for classification.
The results are appended to the original file with additional columns indicating SDG relevance."""

description_label = tk.Label(root, text=description_text, justify=tk.LEFT, wraplength=800)
description_label.grid(row=9, column=0, columnspan=6, sticky='w', padx=10, pady=10)

# Add a button in your Tkinter app to open PandasGUI
pandasgui_button = tk.Button(root, text="Open in PandasGUI", command=open_pandasgui)
pandasgui_button.grid(row=9, column=1, pady=10)


# Run the application
root.mainloop()

# Update the dropdown menu initially with the current file
update_column_dropdown()
