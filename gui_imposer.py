#!/usr/bin/env python3
"""
GUI PDF Imposition Tool for Company Use
Simple interface for PDF imposition
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from company_pdf_imposer import CompanyPDFImposer

class PDFImposerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Company PDF Imposition Tool")
        self.root.geometry("600x500")
        
        self.imposer = CompanyPDFImposer()
        self.input_files = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input files section
        ttk.Label(main_frame, text="Input PDF Files:", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        files_frame = ttk.Frame(main_frame)
        files_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.files_listbox = tk.Listbox(files_frame, height=4)
        self.files_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        files_scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        files_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        files_frame.columnconfigure(0, weight=1)
        
        # Buttons for file management
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=(0, 15))
        
        ttk.Button(btn_frame, text="Add PDF Files", command=self.add_files).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_file).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).grid(row=0, column=2, padx=(5, 0))
        
        # Layout selection
        ttk.Label(main_frame, text="Layout:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.layout_var = tk.StringVar(value="8x2")
        layout_combo = ttk.Combobox(main_frame, textvariable=self.layout_var, state="readonly", width=20)
        layout_combo['values'] = list(self.imposer.layouts.keys())
        layout_combo.grid(row=4, column=0, sticky=tk.W, pady=(0, 10))
        
        # Paper size selection
        ttk.Label(main_frame, text="Paper Size:", font=('Arial', 10, 'bold')).grid(row=3, column=1, sticky=tk.W, pady=(0, 5))
        
        self.paper_var = tk.StringVar(value="A4")
        paper_combo = ttk.Combobox(main_frame, textvariable=self.paper_var, state="readonly", width=15)
        paper_combo['values'] = list(self.imposer.paper_sizes.keys())
        paper_combo.grid(row=4, column=1, sticky=tk.W, pady=(0, 10))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Orientation
        self.landscape_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Landscape orientation", variable=self.landscape_var).grid(row=0, column=0, sticky=tk.W)
        
        # Margin
        ttk.Label(options_frame, text="Margin (mm):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.margin_var = tk.StringVar(value="5")
        margin_entry = ttk.Entry(options_frame, textvariable=self.margin_var, width=10)
        margin_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # DPI
        ttk.Label(options_frame, text="DPI:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.dpi_var = tk.StringVar(value="300")
        dpi_entry = ttk.Entry(options_frame, textvariable=self.dpi_var, width=10)
        dpi_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        
        # Output section
        ttk.Label(main_frame, text="Output File:", font=('Arial', 12, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1, padx=(10, 0))
        
        output_frame.columnconfigure(0, weight=1)
        
        # Process button
        self.process_btn = ttk.Button(main_frame, text="Create Imposed PDF", command=self.process_files)
        self.process_btn.grid(row=8, column=0, columnspan=2, pady=15)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=10, column=0, columnspan=2)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def add_files(self):
        """Add PDF files to the list"""
        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        for file in files:
            if file not in self.input_files:
                self.input_files.append(file)
                self.files_listbox.insert(tk.END, os.path.basename(file))
    
    def remove_file(self):
        """Remove selected file from the list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            del self.input_files[index]
    
    def clear_files(self):
        """Clear all files from the list"""
        self.files_listbox.delete(0, tk.END)
        self.input_files.clear()
    
    def browse_output(self):
        """Browse for output file location"""
        file = filedialog.asksaveasfilename(
            title="Save Imposed PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file:
            self.output_var.set(file)
    
    def process_files(self):
        """Process the files in a separate thread"""
        if not self.input_files:
            messagebox.showerror("Error", "Please select input PDF files")
            return
        
        if not self.output_var.get():
            messagebox.showerror("Error", "Please specify output file")
            return
        
        try:
            margin = float(self.margin_var.get())
            dpi = int(self.dpi_var.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid margin or DPI value")
            return
        
        # Disable button and start progress
        self.process_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Processing...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._process_thread, args=(margin, dpi))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, margin, dpi):
        """Process files in background thread"""
        try:
            success = self.imposer.create_imposition(
                input_files=self.input_files,
                output_path=self.output_var.get(),
                layout=self.layout_var.get(),
                paper_size=self.paper_var.get(),
                margin_mm=margin,
                landscape=self.landscape_var.get(),
                dpi=dpi
            )
            
            # Update UI in main thread
            self.root.after(0, self._process_complete, success)
            
        except Exception as e:
            self.root.after(0, self._process_error, str(e))
    
    def _process_complete(self, success):
        """Handle process completion"""
        self.progress.stop()
        self.process_btn.config(state='normal')
        
        if success:
            self.status_var.set("✅ Imposition completed successfully!")
            messagebox.showinfo("Success", f"Imposed PDF created:\n{self.output_var.get()}")
        else:
            self.status_var.set("❌ Imposition failed")
            messagebox.showerror("Error", "Imposition failed. Check the log for details.")
    
    def _process_error(self, error_msg):
        """Handle process error"""
        self.progress.stop()
        self.process_btn.config(state='normal')
        self.status_var.set("❌ Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")

def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = PDFImposerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()