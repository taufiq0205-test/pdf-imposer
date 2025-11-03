#!/usr/bin/env python3
"""
Simplified GUI PDF Imposition Tool
Easier to debug version with better error handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import traceback
import threading

# Add error handling for imports
try:
    from company_pdf_imposer import CompanyPDFImposer
except ImportError as e:
    print(f"Error importing company_pdf_imposer: {e}")
    print("Make sure company_pdf_imposer.py is in the same directory")
    sys.exit(1)

class SimplePDFImposerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Imposition Tool")
        self.root.geometry("500x400")
        
        # Initialize imposer
        try:
            self.imposer = CompanyPDFImposer()
            print("✅ CompanyPDFImposer initialized")
        except Exception as e:
            print(f"❌ Error initializing CompanyPDFImposer: {e}")
            messagebox.showerror("Initialization Error", f"Failed to initialize PDF imposer:\n{e}")
            return
        
        self.input_files = []
        self.setup_ui()
        print("✅ GUI setup completed")
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Imposition Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Input files section
        files_frame = ttk.LabelFrame(main_frame, text="Input PDF Files", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list
        self.files_listbox = tk.Listbox(files_frame, height=6)
        self.files_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File buttons
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.pack(fill=tk.X)
        
        ttk.Button(file_btn_frame, text="Add PDF Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_btn_frame, text="Clear All", 
                  command=self.clear_files).pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Layout selection
        layout_frame = ttk.Frame(settings_frame)
        layout_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(layout_frame, text="Layout:").pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value="8x2")
        layout_combo = ttk.Combobox(layout_frame, textvariable=self.layout_var, 
                                   state="readonly", width=15)
        layout_combo['values'] = list(self.imposer.layouts.keys())
        layout_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Paper size selection
        paper_frame = ttk.Frame(settings_frame)
        paper_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(paper_frame, text="Paper Size:").pack(side=tk.LEFT)
        self.paper_var = tk.StringVar(value="A4")
        paper_combo = ttk.Combobox(paper_frame, textvariable=self.paper_var, 
                                  state="readonly", width=15)
        paper_combo['values'] = list(self.imposer.paper_sizes.keys())
        paper_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Output section
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_path_frame, text="Output File:").pack(side=tk.LEFT)
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(output_path_frame, textvariable=self.output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        ttk.Button(output_path_frame, text="Browse", 
                  command=self.browse_output).pack(side=tk.RIGHT)
        
        # Process button
        self.process_btn = ttk.Button(output_frame, text="Create Imposed PDF", 
                                     command=self.process_files)
        self.process_btn.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(output_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(output_frame, textvariable=self.status_var)
        status_label.pack()
    
    def add_files(self):
        """Add PDF files to the list"""
        try:
            files = filedialog.askopenfilenames(
                title="Select PDF Files",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            for file in files:
                if file not in self.input_files:
                    self.input_files.append(file)
                    self.files_listbox.insert(tk.END, os.path.basename(file))
            
            print(f"Added {len(files)} files")
            
        except Exception as e:
            print(f"Error adding files: {e}")
            messagebox.showerror("Error", f"Failed to add files:\n{e}")
    
    def clear_files(self):
        """Clear all files from the list"""
        self.files_listbox.delete(0, tk.END)
        self.input_files.clear()
        print("Cleared all files")
    
    def browse_output(self):
        """Browse for output file location"""
        try:
            file = filedialog.asksaveasfilename(
                title="Save Imposed PDF As",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
            
            if file:
                self.output_var.set(file)
                print(f"Output file set to: {file}")
                
        except Exception as e:
            print(f"Error browsing output: {e}")
            messagebox.showerror("Error", f"Failed to browse output:\n{e}")
    
    def process_files(self):
        """Process the files"""
        if not self.input_files:
            messagebox.showerror("Error", "Please select input PDF files")
            return
        
        if not self.output_var.get():
            messagebox.showerror("Error", "Please specify output file")
            return
        
        print(f"Starting processing with {len(self.input_files)} files")
        print(f"Layout: {self.layout_var.get()}")
        print(f"Paper: {self.paper_var.get()}")
        print(f"Output: {self.output_var.get()}")
        
        # Disable button and start progress
        self.process_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Processing...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()
    
    def _process_thread(self):
        """Process files in background thread"""
        try:
            print("Processing in background thread...")
            
            success = self.imposer.create_imposition(
                input_files=self.input_files,
                output_path=self.output_var.get(),
                layout=self.layout_var.get(),
                paper_size=self.paper_var.get(),
                margin_mm=5,
                landscape=True,
                dpi=300
            )
            
            print(f"Processing completed: {success}")
            
            # Update UI in main thread
            self.root.after(0, self._process_complete, success)
            
        except Exception as e:
            print(f"Processing error: {e}")
            traceback.print_exc()
            self.root.after(0, self._process_error, str(e))
    
    def _process_complete(self, success):
        """Handle process completion"""
        self.progress.stop()
        self.process_btn.config(state='normal')
        
        if success:
            self.status_var.set("✅ Completed successfully!")
            messagebox.showinfo("Success", f"Imposed PDF created:\n{self.output_var.get()}")
            print("✅ Processing completed successfully")
        else:
            self.status_var.set("❌ Processing failed")
            messagebox.showerror("Error", "Processing failed. Check the console for details.")
            print("❌ Processing failed")
    
    def _process_error(self, error_msg):
        """Handle process error"""
        self.progress.stop()
        self.process_btn.config(state='normal')
        self.status_var.set("❌ Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")
        print(f"❌ Error: {error_msg}")

def main():
    """Main function to run the GUI"""
    print("Starting Simple PDF Imposer GUI...")
    
    try:
        root = tk.Tk()
        print("✅ Tkinter root created")
        
        app = SimplePDFImposerGUI(root)
        print("✅ GUI application created")
        
        print("Starting main loop...")
        root.mainloop()
        print("✅ GUI closed normally")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()
        
        # Show error in message box if possible
        try:
            messagebox.showerror("Fatal Error", f"Failed to start GUI:\n{e}")
        except:
            pass

if __name__ == "__main__":
    main()