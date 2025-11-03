#!/usr/bin/env python3
"""
Test script to diagnose GUI issues
"""

import sys
import traceback

print("Starting GUI diagnostics...")

# Test 1: Check Python version
print(f"Python version: {sys.version}")

# Test 2: Test tkinter import
try:
    import tkinter as tk
    print("✅ tkinter imported successfully")
except ImportError as e:
    print(f"❌ tkinter import failed: {e}")
    print("Solution: Install tkinter")
    print("  macOS: brew install python-tk")
    print("  Linux: sudo apt-get install python3-tk")
    sys.exit(1)

# Test 3: Test basic tkinter window
try:
    print("Testing basic tkinter window...")
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    label = tk.Label(root, text="If you see this, tkinter works!")
    label.pack(pady=50)
    
    # Close automatically after 3 seconds
    root.after(3000, root.destroy)
    
    print("✅ Basic tkinter window test - should show for 3 seconds")
    root.mainloop()
    print("✅ Basic tkinter test completed")
    
except Exception as e:
    print(f"❌ Basic tkinter test failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test company_pdf_imposer import
try:
    from company_pdf_imposer import CompanyPDFImposer
    print("✅ company_pdf_imposer imported successfully")
except ImportError as e:
    print(f"❌ company_pdf_imposer import failed: {e}")
    print("Make sure company_pdf_imposer.py is in the same directory")
    sys.exit(1)

# Test 5: Test CompanyPDFImposer creation
try:
    imposer = CompanyPDFImposer()
    print("✅ CompanyPDFImposer created successfully")
    print(f"Available layouts: {list(imposer.layouts.keys())}")
except Exception as e:
    print(f"❌ CompanyPDFImposer creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 All tests passed! GUI should work.")
print("Now testing the actual GUI...")

# Test 6: Test the actual GUI
try:
    from gui_imposer import PDFImposerGUI
    
    root = tk.Tk()
    app = PDFImposerGUI(root)
    
    print("✅ GUI created successfully")
    print("GUI window should be visible now...")
    print("Close the window to complete the test")
    
    root.mainloop()
    print("✅ GUI test completed successfully")
    
except Exception as e:
    print(f"❌ GUI test failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All diagnostics completed successfully!")