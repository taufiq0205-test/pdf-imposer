#!/usr/bin/env python3
"""
Debug version of GUI with forced visibility and error handling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import traceback

def main():
    """Main function with comprehensive error handling"""
    
    print("=" * 50)
    print("DEBUG GUI STARTING")
    print("=" * 50)
    
    try:
        # Import with error handling
        print("1. Importing company_pdf_imposer...")
        from company_pdf_imposer import CompanyPDFImposer
        print("✅ Import successful")
        
        # Create root window
        print("2. Creating tkinter root...")
        root = tk.Tk()
        root.title("DEBUG: PDF Imposition Tool")
        root.geometry("600x500")
        
        # Force window to front
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        print("✅ Root window created")
        
        # Create imposer
        print("3. Creating CompanyPDFImposer...")
        imposer = CompanyPDFImposer()
        print("✅ CompanyPDFImposer created")
        
        # Create simple interface
        print("4. Creating interface...")
        
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="DEBUG: PDF Imposition Tool", 
                         font=('Arial', 16, 'bold'))
        title.pack(pady=20)
        
        # Status
        status_text = tk.Text(main_frame, height=10, width=60)
        status_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add some debug info
        debug_info = f"""DEBUG INFORMATION:
Python Version: {sys.version}
Tkinter Available: ✅
CompanyPDFImposer: ✅
Available Layouts: {list(imposer.layouts.keys())}
Available Paper Sizes: {list(imposer.paper_sizes.keys())}

This window should be visible and on top.
If you can see this, the GUI is working!

Close this window to test the main GUI.
"""
        
        status_text.insert(tk.END, debug_info)
        status_text.config(state=tk.DISABLED)
        
        # Test button
        def test_function():
            messagebox.showinfo("Test", "Button clicked! GUI is responsive.")
        
        test_btn = ttk.Button(main_frame, text="Test Button - Click Me!", 
                             command=test_function)
        test_btn.pack(pady=10)
        
        # Close button
        def close_and_test():
            root.destroy()
            print("5. Debug window closed, testing main GUI...")
            test_main_gui()
        
        close_btn = ttk.Button(main_frame, text="Close and Test Main GUI", 
                              command=close_and_test)
        close_btn.pack(pady=5)
        
        print("✅ Interface created")
        print("5. Starting main loop...")
        print("   Window should be visible now!")
        
        # Make sure window is visible
        root.update()
        root.deiconify()
        root.focus_force()
        
        root.mainloop()
        print("✅ Debug GUI completed")
        
    except Exception as e:
        print(f"❌ FATAL ERROR in debug GUI: {e}")
        traceback.print_exc()
        
        # Try to show error dialog
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            messagebox.showerror("Fatal Error", f"Debug GUI failed:\n{e}\n\nCheck console for details.")
            root.destroy()
        except:
            print("Could not show error dialog")

def test_main_gui():
    """Test the main GUI"""
    print("\n" + "=" * 50)
    print("TESTING MAIN GUI")
    print("=" * 50)
    
    try:
        print("Importing gui_imposer...")
        from gui_imposer import PDFImposerGUI
        
        print("Creating main GUI...")
        root = tk.Tk()
        
        # Force visibility
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        
        app = PDFImposerGUI(root)
        
        print("✅ Main GUI created successfully!")
        print("Main GUI window should be visible now...")
        
        root.mainloop()
        print("✅ Main GUI completed")
        
    except Exception as e:
        print(f"❌ Main GUI failed: {e}")
        traceback.print_exc()
        
        try:
            messagebox.showerror("Main GUI Error", f"Main GUI failed:\n{e}")
        except:
            pass

if __name__ == "__main__":
    main()