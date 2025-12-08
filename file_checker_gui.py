import hashlib
import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import threading

class FileIntegrityChecker:
    def __init__(self, baseline_file="baseline.json"):
        self.baseline_file = baseline_file
        self.baseline_data = {}
    
    def calculate_hash(self, filepath, algorithm="sha256"):
        hash_func = hashlib.new(algorithm)
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            return None
    
    def scan_directory(self, directory, algorithm="sha256", progress_callback=None):
        file_data = {}
        directory_path = Path(directory)
        
        if not directory_path.exists():
            return file_data
        
        all_files = list(directory_path.rglob('*'))
        total_files = len([f for f in all_files if f.is_file()])
        current = 0
        
        for filepath in all_files:
            if filepath.is_file():
                try:
                    file_stats = filepath.stat()
                    file_hash = self.calculate_hash(filepath, algorithm)
                    
                    if file_hash:
                        relative_path = str(filepath.relative_to(directory_path))
                        file_data[relative_path] = {
                            'hash': file_hash,
                            'size': file_stats.st_size,
                            'modified': file_stats.st_mtime,
                            'algorithm': algorithm
                        }
                        current += 1
                        if progress_callback:
                            progress_callback(current, total_files, relative_path)
                
                except Exception as e:
                    pass
        
        return file_data
    
    def create_baseline(self, directory, algorithm="sha256", progress_callback=None):
        self.baseline_data = self.scan_directory(directory, algorithm, progress_callback)
        
        baseline_info = {
            'created': datetime.now().isoformat(),
            'directory': str(directory),
            'algorithm': algorithm,
            'files': self.baseline_data
        }
        
        try:
            with open(self.baseline_file, 'w') as f:
                json.dump(baseline_info, f, indent=4)
            return True, len(self.baseline_data)
        except Exception as e:
            return False, str(e)
    
    def load_baseline(self):
        try:
            with open(self.baseline_file, 'r') as f:
                baseline_info = json.load(f)
                self.baseline_data = baseline_info['files']
                return True, baseline_info
        except FileNotFoundError:
            return False, "Baseline file not found"
        except Exception as e:
            return False, str(e)
    
    def verify_integrity(self, directory, progress_callback=None):
        success, baseline_info = self.load_baseline()
        if not success:
            return False, baseline_info, None, None, None
        
        algorithm = list(self.baseline_data.values())[0]['algorithm'] if self.baseline_data else 'sha256'
        current_data = self.scan_directory(directory, algorithm, progress_callback)
        
        modified = []
        added = []
        deleted = []
        
        for filename, baseline_info_file in self.baseline_data.items():
            if filename not in current_data:
                deleted.append(filename)
            elif current_data[filename]['hash'] != baseline_info_file['hash']:
                modified.append(filename)
        
        for filename in current_data:
            if filename not in self.baseline_data:
                added.append(filename)
        
        return True, modified, added, deleted


class FileIntegrityGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Integrity Checker")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.checker = FileIntegrityChecker()
        self.selected_directory = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 File Integrity Checker", 
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Directory selection frame
        dir_frame = ttk.LabelFrame(main_frame, text="Directory Selection", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(1, weight=1)
        
        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.selected_directory, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        
        browse_btn = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Hash algorithm selection
        ttk.Label(dir_frame, text="Algorithm:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        
        self.algorithm_var = tk.StringVar(value="sha256")
        algorithm_combo = ttk.Combobox(dir_frame, textvariable=self.algorithm_var, 
                                      values=["md5", "sha1", "sha256", "sha512"], 
                                      state="readonly", width=15)
        algorithm_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        self.create_btn = ttk.Button(button_frame, text="Create Baseline", 
                                     command=self.create_baseline_thread, width=20)
        self.create_btn.grid(row=0, column=0, padx=5)
        
        self.verify_btn = ttk.Button(button_frame, text="Verify Integrity", 
                                     command=self.verify_integrity_thread, width=20)
        self.verify_btn.grid(row=0, column=1, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Output", 
                                    command=self.clear_output, width=15)
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, mode='determinate')
        self.progress_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=4, column=0, sticky=tk.W)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                     height=20, font=('Consolas', 10))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure text tags for colored output
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("warning", foreground="orange")
        self.output_text.tag_config("info", foreground="blue")
        self.output_text.tag_config("header", font=('Consolas', 10, 'bold'))
        
        self.log("Welcome to File Integrity Checker! 🔒\n", "header")
        self.log("Select a directory and create a baseline to get started.\n", "info")

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.selected_directory.set(directory)
            self.log(f"\nSelected directory: {directory}\n", "info")
    
    def log(self, message, tag="normal"):
        self.output_text.insert(tk.END, message, tag)
        self.output_text.see(tk.END)
        self.output_text.update()
    
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.log("Output cleared.\n", "info")
    
    def update_progress(self, current, total, filename):
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(text=f"Processing: {filename} ({current}/{total})")
            self.root.update_idletasks()
    
    def disable_buttons(self):
        self.create_btn.config(state='disabled')
        self.verify_btn.config(state='disabled')
    
    def enable_buttons(self):
        self.create_btn.config(state='normal')
        self.verify_btn.config(state='normal')
