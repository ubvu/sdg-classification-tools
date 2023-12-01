import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yaml
import threading
import os  # Import the os module
import pandas as pd  # Import pandas to read the CSV file for record count
import sdg_csv  # Assuming sdg_csv.py is the module name of your script

# Global variable to keep track of the classification state
is_classifying = False

# Function to load config settings
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

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
def start_classification(input_file, output_folder, model_url, threshold, rate_limit):
    global is_classifying
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    sdg_csv.process_csv(input_file, output_folder, threshold, model_url, input_base_name, rate_limit, update_progress)
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
    threading.Thread(target=start_classification, args=(input_file, output_folder, model_url, threshold, rate_limit)).start()

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
tk.Label(root, text="Select Input File:").grid(row=0, column=0, sticky='w')
file_input = tk.StringVar(value=config['data_input_folder'] + config['data_input_file'])
tk.Entry(root, textvariable=file_input, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse...", command=lambda: file_input.set(filedialog.askopenfilename())).grid(row=0, column=2)

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

# Run the application
root.mainloop()
