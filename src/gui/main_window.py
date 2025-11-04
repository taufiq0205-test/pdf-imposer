#!/usr/bin/env python3
"""
Enhanced GUI PDF Imposition Tool
Features: Custom paper sizes, real-time preview, advanced settings
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from PIL import Image, ImageTk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.core.imposer import CompanyPDFImposer

class EnhancedPDFImposerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced PDF Imposition Tool")
        self.root.geometry("900x700")
        
        self.imposer = CompanyPDFImposer()
        self.input_files = []
        self.preview_image = None
        self.preview_path = None
        
        self.setup_ui()
        self.update_preview()
    
    def setup_ui(self):
        """Setup the enhanced user interface"""
        
        # Create main paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel for controls
        left_frame = ttk.Frame(main_paned, padding="10")
        main_paned.add(left_frame, weight=1)
        
        # Right panel for preview
        right_frame = ttk.Frame(main_paned, padding="10")
        main_paned.add(right_frame, weight=1)
        
        self.setup_left_panel(left_frame)
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        """Setup the left control panel"""
        
        # Title
        title_label = ttk.Label(parent, text="PDF Imposition Tool", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Input files section
        files_frame = ttk.LabelFrame(parent, text="Input PDF Files", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # File list with scrollbar
        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.files_listbox = tk.Listbox(list_frame, height=6)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # File buttons
        file_btn_frame = ttk.Frame(files_frame)
        file_btn_frame.pack(fill=tk.X)
        
        ttk.Button(file_btn_frame, text="Add PDF Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_btn_frame, text="Remove Selected", 
                  command=self.remove_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_btn_frame, text="Clear All", 
                  command=self.clear_files).pack(side=tk.LEFT)
        
        # Layout settings
        layout_frame = ttk.LabelFrame(parent, text="Layout Settings", padding="10")
        layout_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Layout selection
        layout_row1 = ttk.Frame(layout_frame)
        layout_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(layout_row1, text="Layout:").pack(side=tk.LEFT)
        self.layout_var = tk.StringVar(value="8x2")
        self.layout_combo = ttk.Combobox(layout_row1, textvariable=self.layout_var, 
                                        state="readonly", width=15)
        self.layout_combo['values'] = list(self.imposer.layouts.keys())
        self.layout_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.layout_combo.bind('<<ComboboxSelected>>', self.on_layout_change)
        
        # Exact method indicator
        self.exact_method_var = tk.StringVar(value="✅ Using exact method")
        self.exact_method_label = ttk.Label(layout_row1, textvariable=self.exact_method_var, 
                                           font=('Arial', 9), foreground='green')
        self.exact_method_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Custom layout settings (initially hidden)
        self.custom_layout_frame = ttk.Frame(layout_frame)
        
        custom_row1 = ttk.Frame(self.custom_layout_frame)
        custom_row1.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(custom_row1, text="Columns:").pack(side=tk.LEFT)
        self.custom_cols_var = tk.StringVar(value="8")
        cols_entry = ttk.Entry(custom_row1, textvariable=self.custom_cols_var, width=5)
        cols_entry.pack(side=tk.LEFT, padx=(10, 20))
        cols_entry.bind('<KeyRelease>', self.on_setting_change)
        
        ttk.Label(custom_row1, text="Rows:").pack(side=tk.LEFT)
        self.custom_rows_var = tk.StringVar(value="2")
        rows_entry = ttk.Entry(custom_row1, textvariable=self.custom_rows_var, width=5)
        rows_entry.pack(side=tk.LEFT, padx=(10, 0))
        rows_entry.bind('<KeyRelease>', self.on_setting_change)
        
        # Paper size settings
        paper_frame = ttk.LabelFrame(parent, text="Paper Settings", padding="10")
        paper_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Paper size selection
        paper_row1 = ttk.Frame(paper_frame)
        paper_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(paper_row1, text="Paper Size:").pack(side=tk.LEFT)
        self.paper_var = tk.StringVar(value="A4")
        self.paper_combo = ttk.Combobox(paper_row1, textvariable=self.paper_var, 
                                       state="readonly", width=15)
        self.paper_combo['values'] = list(self.imposer.paper_sizes.keys())
        self.paper_combo.pack(side=tk.LEFT, padx=(10, 0))
        self.paper_combo.bind('<<ComboboxSelected>>', self.on_paper_change)
        
        # Custom paper size settings (initially hidden)
        self.custom_paper_frame = ttk.Frame(paper_frame)
        
        custom_paper_row1 = ttk.Frame(self.custom_paper_frame)
        custom_paper_row1.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(custom_paper_row1, text="Width (mm):").pack(side=tk.LEFT)
        self.custom_width_var = tk.StringVar(value="210")
        width_entry = ttk.Entry(custom_paper_row1, textvariable=self.custom_width_var, width=8)
        width_entry.pack(side=tk.LEFT, padx=(10, 20))
        width_entry.bind('<KeyRelease>', self.on_setting_change)
        
        ttk.Label(custom_paper_row1, text="Height (mm):").pack(side=tk.LEFT)
        self.custom_height_var = tk.StringVar(value="297")
        height_entry = ttk.Entry(custom_paper_row1, textvariable=self.custom_height_var, width=8)
        height_entry.pack(side=tk.LEFT, padx=(10, 0))
        height_entry.bind('<KeyRelease>', self.on_setting_change)
        
        # Orientation
        orientation_row = ttk.Frame(paper_frame)
        orientation_row.pack(fill=tk.X, pady=(5, 0))
        
        self.landscape_var = tk.BooleanVar(value=True)
        landscape_cb = ttk.Checkbutton(orientation_row, text="Landscape orientation", 
                                      variable=self.landscape_var, 
                                      command=self.on_setting_change)
        landscape_cb.pack(side=tk.LEFT)
        
        # Advanced options
        options_frame = ttk.LabelFrame(parent, text="Advanced Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Margin and DPI
        options_row1 = ttk.Frame(options_frame)
        options_row1.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(options_row1, text="Margin (mm):").pack(side=tk.LEFT)
        self.margin_var = tk.StringVar(value="5")
        margin_entry = ttk.Entry(options_row1, textvariable=self.margin_var, width=8)
        margin_entry.pack(side=tk.LEFT, padx=(10, 20))
        margin_entry.bind('<KeyRelease>', self.on_setting_change)
        
        ttk.Label(options_row1, text="DPI:").pack(side=tk.LEFT)
        self.dpi_var = tk.StringVar(value="300")
        dpi_entry = ttk.Entry(options_row1, textvariable=self.dpi_var, width=8)
        dpi_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Output section
        output_frame = ttk.LabelFrame(parent, text="Output", padding="10")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Output path
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(output_path_frame, text="Output File:").pack(anchor=tk.W)
        
        path_entry_frame = ttk.Frame(output_path_frame)
        path_entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(path_entry_frame, textvariable=self.output_var)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(path_entry_frame, text="Browse", 
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
    
    def setup_right_panel(self, parent):
        """Setup the right preview panel"""
        
        # Preview title
        preview_title = ttk.Label(parent, text="Layout Preview", 
                                 font=('Arial', 14, 'bold'))
        preview_title.pack(pady=(0, 10))
        
        # Preview frame with scrollbars
        preview_frame = ttk.Frame(parent)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for preview with scrollbars
        canvas_frame = ttk.Frame(preview_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_canvas = tk.Canvas(canvas_frame, bg='white', 
                                       scrollregion=(0, 0, 400, 300))
        
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, 
                                   command=self.preview_canvas.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, 
                                   command=self.preview_canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.preview_canvas.configure(yscrollcommand=v_scrollbar.set,
                                     xscrollcommand=h_scrollbar.set)
        
        # Preview info
        self.preview_info_var = tk.StringVar(value="No files selected")
        info_label = ttk.Label(parent, textvariable=self.preview_info_var, 
                              font=('Arial', 10))
        info_label.pack(pady=(10, 0))
        
        # Method info
        self.method_info_var = tk.StringVar(value="8x2 layout uses exact method from pdf_impose_single_final.py")
        method_info_label = ttk.Label(parent, textvariable=self.method_info_var, 
                                     font=('Arial', 9), foreground='blue')
        method_info_label.pack(pady=(5, 0))
        
        # Refresh preview button
        ttk.Button(parent, text="Refresh Preview", 
                  command=self.update_preview).pack(pady=(5, 0))
    
    def on_layout_change(self, event=None):
        """Handle layout selection change"""
        layout = self.layout_var.get()
        
        if layout == 'custom':
            self.custom_layout_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.custom_layout_frame.pack_forget()
        
        # Update exact method indicator
        if layout == '8x2':
            self.exact_method_var.set("✅ Using exact method")
            self.exact_method_label.configure(foreground='green')
            self.method_info_var.set("8x2 layout uses exact method from pdf_impose_single_final.py\nGuarantees identical quality and dimensions")
        else:
            self.exact_method_var.set("Standard method")
            self.exact_method_label.configure(foreground='gray')
            self.method_info_var.set("Using standard imposition method with configurable settings")
        
        self.on_setting_change()
    
    def on_paper_change(self, event=None):
        """Handle paper size selection change"""
        if self.paper_var.get() == 'Custom':
            self.custom_paper_frame.pack(fill=tk.X, pady=(5, 0))
        else:
            self.custom_paper_frame.pack_forget()
        self.on_setting_change()
    
    def on_setting_change(self, event=None):
        """Handle any setting change - update preview"""
        # Debounce the preview update
        if hasattr(self, '_update_timer'):
            self.root.after_cancel(self._update_timer)
        self._update_timer = self.root.after(500, self.update_preview)
    
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
        
        if files:
            self.update_preview()
    
    def remove_file(self):
        """Remove selected file from the list"""
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            del self.input_files[index]
            self.update_preview()
    
    def clear_files(self):
        """Clear all files from the list"""
        self.files_listbox.delete(0, tk.END)
        self.input_files.clear()
        self.update_preview()
    
    def browse_output(self):
        """Browse for output file location"""
        file = filedialog.asksaveasfilename(
            title="Save Imposed PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file:
            self.output_var.set(file)
    
    def update_preview(self):
        """Update the preview image"""
        if not self.input_files:
            self.preview_canvas.delete("all")
            self.preview_info_var.set("No files selected")
            return
        
        # Run preview generation in background
        thread = threading.Thread(target=self._generate_preview_thread)
        thread.daemon = True
        thread.start()
    
    def _generate_preview_thread(self):
        """Generate preview in background thread"""
        try:
            # Get current settings
            layout = self.layout_var.get()
            paper_size = self.paper_var.get()
            landscape = self.landscape_var.get()
            
            # Get custom settings if needed
            custom_cols = 0
            custom_rows = 0
            if layout == 'custom':
                try:
                    custom_cols = int(self.custom_cols_var.get())
                    custom_rows = int(self.custom_rows_var.get())
                except ValueError:
                    custom_cols = custom_rows = 0
            
            custom_width_mm = 0
            custom_height_mm = 0
            if paper_size == 'Custom':
                try:
                    custom_width_mm = float(self.custom_width_var.get())
                    custom_height_mm = float(self.custom_height_var.get())
                except ValueError:
                    custom_width_mm = custom_height_mm = 0
            
            # Special handling for 8x2 layout preview
            if layout == '8x2':
                print("Generating preview using exact 8x2 method")
                # For 8x2 preview, we'll use the exact dimensions
                preview_path = self.imposer.generate_preview(
                    input_files=self.input_files,
                    layout=layout,
                    paper_size='A4',  # The exact method uses fixed dimensions anyway
                    custom_cols=custom_cols,
                    custom_rows=custom_rows,
                    custom_width_mm=custom_width_mm,
                    custom_height_mm=custom_height_mm,
                    landscape=True  # 8x2 is always landscape in the exact method
                )
            else:
                # Generate preview for other layouts
                preview_path = self.imposer.generate_preview(
                    input_files=self.input_files,
                    layout=layout,
                    paper_size=paper_size,
                    custom_cols=custom_cols,
                    custom_rows=custom_rows,
                    custom_width_mm=custom_width_mm,
                    custom_height_mm=custom_height_mm,
                    landscape=landscape
                )
            
            # Update UI in main thread
            self.root.after(0, self._update_preview_display, preview_path)
            
        except Exception as e:
            self.root.after(0, self._preview_error, str(e))
    
    def _update_preview_display(self, preview_path):
        """Update preview display in main thread"""
        if preview_path and os.path.exists(preview_path):
            try:
                # Load and display preview image
                img = Image.open(preview_path)
                
                # Scale image to fit canvas
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width > 1 and canvas_height > 1:
                    # Calculate scaling
                    scale_x = (canvas_width - 20) / img.width
                    scale_y = (canvas_height - 20) / img.height
                    scale = min(scale_x, scale_y, 1.0)  # Don't scale up
                    
                    new_width = int(img.width * scale)
                    new_height = int(img.height * scale)
                    
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                self.preview_image = ImageTk.PhotoImage(img)
                
                # Clear canvas and add image
                self.preview_canvas.delete("all")
                self.preview_canvas.create_image(
                    self.preview_canvas.winfo_width() // 2,
                    self.preview_canvas.winfo_height() // 2,
                    image=self.preview_image,
                    anchor=tk.CENTER
                )
                
                # Update scroll region
                self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
                
                # Update info
                layout_info = self.get_layout_info()
                self.preview_info_var.set(f"Preview: {layout_info}")
                
            except Exception as e:
                self._preview_error(f"Display error: {e}")
        else:
            self._preview_error("Preview generation failed")
    
    def _preview_error(self, error_msg):
        """Handle preview error"""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            self.preview_canvas.winfo_width() // 2,
            self.preview_canvas.winfo_height() // 2,
            text=f"Preview Error:\n{error_msg}",
            anchor=tk.CENTER,
            fill="red"
        )
        self.preview_info_var.set("Preview error")
    
    def get_layout_info(self):
        """Get current layout information string"""
        layout = self.layout_var.get()
        paper = self.paper_var.get()
        
        if layout == 'custom':
            try:
                cols = int(self.custom_cols_var.get())
                rows = int(self.custom_rows_var.get())
                layout_str = f"{cols}x{rows}"
            except ValueError:
                layout_str = "custom"
        else:
            layout_str = layout
        
        if paper == 'Custom':
            try:
                width = float(self.custom_width_var.get())
                height = float(self.custom_height_var.get())
                paper_str = f"{width}x{height}mm"
            except ValueError:
                paper_str = "custom"
        else:
            paper_str = paper
        
        orientation = "landscape" if self.landscape_var.get() else "portrait"
        
        return f"{layout_str} on {paper_str} ({orientation})"
    
    def process_files(self):
        """Process the files"""
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
        
        # Get custom settings
        custom_cols = custom_rows = 0
        if self.layout_var.get() == 'custom':
            try:
                custom_cols = int(self.custom_cols_var.get())
                custom_rows = int(self.custom_rows_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid custom layout values")
                return
        
        custom_width_mm = custom_height_mm = 0
        if self.paper_var.get() == 'Custom':
            try:
                custom_width_mm = float(self.custom_width_var.get())
                custom_height_mm = float(self.custom_height_var.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid custom paper size values")
                return
        
        # Disable button and start progress
        self.process_btn.config(state='disabled')
        self.progress.start()
        self.status_var.set("Processing...")
        
        # Run in separate thread
        thread = threading.Thread(target=self._process_thread, 
                                 args=(margin, dpi, custom_cols, custom_rows, 
                                      custom_width_mm, custom_height_mm))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, margin, dpi, custom_cols, custom_rows, 
                       custom_width_mm, custom_height_mm):
        """Process files in background thread"""
        try:
            # Special handling for 8x2 layout to ensure exact method is used
            layout = self.layout_var.get()
            
            if layout == '8x2':
                print("Using exact 8x2 method from updated company_pdf_imposer.py")
                # For 8x2, the exact method will be automatically used
                success = self.imposer.create_imposition(
                    input_files=self.input_files,
                    output_path=self.output_var.get(),
                    layout=layout,
                    paper_size=self.paper_var.get(),
                    margin_mm=5,  # Force 5mm margin for exact 8x2 method
                    landscape=self.landscape_var.get(),
                    dpi=dpi,
                    custom_cols=custom_cols,
                    custom_rows=custom_rows,
                    custom_width_mm=custom_width_mm,
                    custom_height_mm=custom_height_mm
                )
            else:
                # For other layouts, use the provided margin
                success = self.imposer.create_imposition(
                    input_files=self.input_files,
                    output_path=self.output_var.get(),
                    layout=layout,
                    paper_size=self.paper_var.get(),
                    margin_mm=margin,
                    landscape=self.landscape_var.get(),
                    dpi=dpi,
                    custom_cols=custom_cols,
                    custom_rows=custom_rows,
                    custom_width_mm=custom_width_mm,
                    custom_height_mm=custom_height_mm
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
            layout = self.layout_var.get()
            if layout == '8x2':
                self.status_var.set("✅ Completed with exact 8x2 method!")
                messagebox.showinfo("Success", 
                                   f"Imposed PDF created using exact method:\n{self.output_var.get()}\n\n" +
                                   "This uses the identical method as pdf_impose_single_final.py\n" +
                                   "Guaranteed same quality and dimensions!")
            else:
                self.status_var.set("✅ Completed successfully!")
                messagebox.showinfo("Success", f"Imposed PDF created:\n{self.output_var.get()}")
        else:
            self.status_var.set("❌ Processing failed")
            messagebox.showerror("Error", "Processing failed. Check the log for details.")
    
    def _process_error(self, error_msg):
        """Handle process error"""
        self.progress.stop()
        self.process_btn.config(state='normal')
        self.status_var.set("❌ Error occurred")
        messagebox.showerror("Error", f"An error occurred:\n{error_msg}")

def main():
    """Main function to run the enhanced GUI"""
    print("Starting Enhanced PDF Imposition GUI...")
    
    root = tk.Tk()
    
    # Force window to be visible
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    app = EnhancedPDFImposerGUI(root)
    
    print("✅ Enhanced GUI started successfully")
    root.mainloop()
    print("✅ Enhanced GUI closed")

if __name__ == "__main__":
    main()