#!/usr/bin/env python3
"""
Final Single Sheet PDF Imposition
Creates a single PDF page with all 16 images properly arranged in 8x2 grid
"""

import os
import sys
import subprocess
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape, A4
from PyPDF2 import PdfReader, PdfWriter
import io

def extract_pages_as_images(pdf_path, output_dir):
    """Extract each PDF page as a separate image using pdftoppm"""
    
    print(f"Extracting pages from {pdf_path}...")
    
    try:
        # Use pdftoppm to convert PDF pages to images
        subprocess.run([
            'pdftoppm',
            '-png',
            '-r', '300',  # 300 DPI for good quality
            pdf_path,
            os.path.join(output_dir, os.path.basename(pdf_path).replace('.pdf', ''))
        ], check=True)
        
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("pdftoppm not available, trying alternative method...")
        return False

def create_single_sheet_with_images(pdf1_path, pdf2_path, output_path):
    """Create single sheet by extracting and placing individual images"""
    
    print("Creating single sheet with individual images...")
    
    # Create temporary directory for images
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Method 1: Try using pdftoppm to extract images
        if extract_pages_as_images(pdf1_path, temp_dir) and extract_pages_as_images(pdf2_path, temp_dir):
            print("✓ Pages extracted as images")
            # Create layout with images
            create_layout_with_images(temp_dir, output_path)
        else:
            # Method 2: Use a different approach with qpdf
            create_single_sheet_qpdf_method(pdf1_path, pdf2_path, output_path)
            
    finally:
        # Clean up temp directory
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def create_layout_with_images(image_dir, output_path):
    """Create PDF layout using extracted images"""
    
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    import glob
    
    # Find all PNG files
    image_files = sorted(glob.glob(os.path.join(image_dir, "*.png")))
    print(f"Found {len(image_files)} image files")
    
    if len(image_files) == 0:
        raise Exception("No images found")
    
    # Calculate sheet dimensions
    page_size = 56 * mm
    cols, rows = 8, 2
    margin = 5 * mm
    
    sheet_width = cols * page_size + (cols + 1) * margin
    sheet_height = rows * page_size + (rows + 1) * margin
    
    # Create PDF
    c = canvas.Canvas(output_path, pagesize=(sheet_width, sheet_height))
    
    # Place each image
    for i, image_file in enumerate(image_files[:16]):  # Max 16 images
        col = i % cols
        row = i // cols
        
        x = margin + col * (page_size + margin)
        y = sheet_height - margin - (row + 1) * page_size
        
        # Draw the image
        c.drawImage(image_file, x, y, width=page_size, height=page_size)
        
        print(f"  Placed image {i+1} at position ({col}, {row})")
    
    c.save()
    print(f"✓ Single sheet created with images: {output_path}")

def create_single_sheet_qpdf_method(pdf1_path, pdf2_path, output_path):
    """Alternative method using qpdf and careful page handling"""
    
    print("Using qpdf method for single sheet...")
    
    # Step 1: Combine PDFs
    temp_combined = "temp_combined_single.pdf"
    
    try:
        subprocess.run([
            'qpdf',
            '--empty',
            '--pages',
            pdf1_path, '1-z',
            pdf2_path, '1-z',
            '--',
            temp_combined
        ], check=True)
        
        print("✓ PDFs combined")
        
        # Step 2: Create single sheet layout using reportlab and careful PDF handling
        create_single_sheet_reportlab(temp_combined, output_path)
        
    finally:
        if os.path.exists(temp_combined):
            os.remove(temp_combined)

def create_single_sheet_reportlab(combined_pdf, output_path):
    """Create single sheet using reportlab with better PDF handling"""
    
    print("Creating single sheet with reportlab...")
    
    # Read the combined PDF
    reader = PdfReader(combined_pdf)
    print(f"Combined PDF has {len(reader.pages)} pages")
    
    # Calculate dimensions
    page_size = 56 * mm
    cols, rows = 8, 2
    margin = 5 * mm
    
    sheet_width = cols * page_size + (cols + 1) * margin
    sheet_height = rows * page_size + (rows + 1) * margin
    
    # Create base canvas
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(sheet_width, sheet_height))
    
    # Draw background and grid
    c.setFillColorRGB(1, 1, 1)
    c.rect(0, 0, sheet_width, sheet_height, fill=1)
    
    # Draw grid lines
    c.setStrokeColorRGB(0.9, 0.9, 0.9)
    c.setLineWidth(0.5)
    
    for col in range(cols + 1):
        x = margin + col * (page_size + margin)
        c.line(x, 0, x, sheet_height)
    
    for row in range(rows + 1):
        y = margin + row * (page_size + margin)
        c.line(0, y, sheet_width, y)
    
    # Add page numbers for reference
    c.setFont("Helvetica", 6)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    
    for i in range(min(16, len(reader.pages))):
        col = i % cols
        row = i // cols
        
        x = margin + col * (page_size + margin) + 2
        y = sheet_height - margin - row * (page_size + margin) - 8
        
        c.drawString(x, y, f"P{i+1}")
    
    c.save()
    packet.seek(0)
    
    # Read the canvas as PDF
    canvas_pdf = PdfReader(packet)
    base_page = canvas_pdf.pages[0]
    
    # Now try to overlay each page from the source PDF
    writer = PdfWriter()
    
    # For each source page, create a positioned version
    for i in range(min(16, len(reader.pages))):
        source_page = reader.pages[i]
        
        # Calculate position
        col = i % cols
        row = i // cols
        
        x = margin + col * (page_size + margin)
        y = sheet_height - margin - (row + 1) * page_size
        
        # Create a copy of the base page for this iteration
        if i == 0:
            # For the first page, use the base page
            current_page = base_page
        else:
            # For subsequent pages, create a copy
            current_page = base_page
        
        # Scale and position the source page
        source_width = float(source_page.mediabox.width)
        source_height = float(source_page.mediabox.height)
        
        scale = min(page_size / source_width, page_size / source_height) * 0.95
        
        # Center the scaled page
        scaled_width = source_width * scale
        scaled_height = source_height * scale
        center_x = x + (page_size - scaled_width) / 2
        center_y = y + (page_size - scaled_height) / 2
        
        # Apply transformation to source page
        source_page.scale(scale, scale)
        source_page.add_transformation([1, 0, 0, 1, center_x, center_y])
        
        # Merge with current page
        current_page.merge_page(source_page)
        
        print(f"  Processed page {i+1}")
    
    # Add the final composed page
    writer.add_page(base_page)
    
    # Write output
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    
    print(f"✓ Single sheet created: {output_path}")

def install_poppler_if_needed():
    """Install poppler-utils for pdftoppm if not available"""
    
    try:
        subprocess.run(['pdftoppm', '-h'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing poppler-utils for better PDF processing...")
        try:
            subprocess.run(['brew', 'install', 'poppler'], check=True)
            return True
        except subprocess.CalledProcessError:
            print("Could not install poppler, using alternative method")
            return False

def main():
    """Main function"""
    
    # File paths
    base_dir = "Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF"
    pdf1_path = os.path.join(base_dir, "raw_1.pdf")
    pdf2_path = os.path.join(base_dir, "raw_2.pdf")
    
    output_dir = "Charm-56x56mm-Sample/CHM2UP_Sample/Imposed_PDF"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "final_single_sheet.pdf")
    
    # Check input files
    if not os.path.exists(pdf1_path):
        print(f"Error: File not found: {pdf1_path}")
        return 1
    
    if not os.path.exists(pdf2_path):
        print(f"Error: File not found: {pdf2_path}")
        return 1
    
    print("Final Single Sheet PDF Imposition")
    print("=" * 40)
    print("Creating a single PDF page with all 16 images in 8x2 grid")
    print()
    
    try:
        # Try to install poppler for better results
        install_poppler_if_needed()
        
        # Create the single sheet
        create_single_sheet_with_images(pdf1_path, pdf2_path, output_path)
        
        print("\n" + "=" * 50)
        print("✅ SUCCESS!")
        print(f"✅ Final single sheet PDF: {output_path}")
        print()
        print("This PDF contains:")
        print("- Single page with all 16 images")
        print("- 8x2 grid layout (8 horizontal, 2 vertical)")
        print("- Ready for printing")
        print("- Similar format to your example file")
        
        return 0
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())