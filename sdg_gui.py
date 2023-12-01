import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yaml
import threading
import sdg_csv  # Assuming sdg_csv.py is the module name of your script

# Function to load config settings
def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

# Function to provide a live update to the progress bar as each row is processed. 
def update_progress(value):
    progress_bar['value'] = value
    root.update_idletasks()

# Function to start the classification process
def start_classification(input_file, output_folder, model_url, threshold):
    input_base_name = os.path.splitext(os.path.basename(input_file))[0]
    sdg_csv.process_csv(input_file, output_folder, threshold, model_url, input_base_name, update_progress)
    messagebox.showinfo("Complete", "Classification completed successfully.")

# Function to handle the classification process in a separate thread
def classify():
    input_file = file_input.get()
    output_folder = folder_output.get()
    model_url = model_var.get()
    threshold = float(threshold_var.get())
    progress_bar['value'] = 0

    # Start the classification process in a separate thread
    threading.Thread(target=start_classification, args=(input_file, output_folder, model_url, threshold)).start()

# Load config
config = load_config()

# Create the main window
root = tk.Tk()
root.title("SDG Classification")

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

# Classify button
tk.Button(root, text="Classify", command=classify).grid(row=4, column=1)

# Progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
progress_bar.grid(row=5, column=0, columnspan=3, pady=10)

# Run the application
root.mainloop()
