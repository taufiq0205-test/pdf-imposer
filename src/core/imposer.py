#!/usr/bin/env python3
"""
Core PDF Imposition Engine
Main imposition logic and functionality
"""

import os
import sys
import json
import logging
import argparse
import subprocess
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm, inch
from reportlab.lib.pagesizes import A4, A3, A2, A1
from PyPDF2 import PdfReader, PdfWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('imposition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompanyPDFImposer:
    """Company PDF Imposition Tool"""
    
    def __init__(self):
        self.layouts = {
            '2up': {'cols': 2, 'rows': 1, 'description': '2-up (2x1)'},
            '4up': {'cols': 2, 'rows': 2, 'description': '4-up (2x2)'},
            '4up_dup': {'cols': 4, 'rows': 2, 'description': '4-up with duplicate (4x2, 8 total)'},
            '8up': {'cols': 4, 'rows': 2, 'description': '8-up (4x2)'},
            '8x2': {'cols': 8, 'rows': 2, 'description': '8x2 (8 horizontal, 2 vertical)'},
            '16up': {'cols': 4, 'rows': 4, 'description': '16-up (4x4)'},
            'custom': {'cols': 0, 'rows': 0, 'description': 'Custom layout'}
        }
        
        self.paper_sizes = {
            'A4': A4,
            'A3': A3, 
            'A2': A2,
            'A1': A1,
            'Letter': (8.5*inch, 11*inch),
            'Legal': (8.5*inch, 14*inch),
            'Tabloid': (11*inch, 17*inch),
            'Custom': (0, 0)  # Will be set dynamically
        }
        
        self.temp_dir = None
        self.custom_paper_size = None
    
    def setup_temp_directory(self):
        """Create temporary directory for processing"""
        self.temp_dir = tempfile.mkdtemp(prefix='company_imposition_')
        logger.info(f"Created temp directory: {self.temp_dir}")
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up temporary files")
    
    def extract_pages_as_images(self, pdf_path: str, dpi: int = 300) -> List[str]:
        """Extract PDF pages as high-quality images"""
        logger.info(f"Extracting pages from {pdf_path}")
        
        base_name = Path(pdf_path).stem
        output_prefix = os.path.join(self.temp_dir, base_name)
        
        try:
            subprocess.run([
                'pdftoppm',
                '-png',
                '-r', str(dpi),
                pdf_path,
                output_prefix
            ], check=True, capture_output=True)
            
            # Find generated images
            import glob
            image_files = sorted(glob.glob(f"{output_prefix}-*.png"))
            logger.info(f"Extracted {len(image_files)} pages as images")
            return image_files
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract images: {e}")
            return []
        except FileNotFoundError:
            logger.error("pdftoppm not found. Please install poppler-utils.")
            return []
    
    def create_imposition(self, 
                         input_files: List[str],
                         output_path: str,
                         layout: str = '8x2',
                         paper_size: str = 'A4',
                         margin_mm: float = 5,
                         landscape: bool = True,
                         dpi: int = 300,
                         custom_cols: int = 0,
                         custom_rows: int = 0,
                         custom_width_mm: float = 0,
                         custom_height_mm: float = 0) -> bool:
        """Create imposed PDF"""
        
        logger.info(f"Starting imposition job")
        logger.info(f"Layout: {layout}")
        logger.info(f"Paper: {paper_size}")
        logger.info(f"Input files: {len(input_files)}")
        logger.info(f"Output: {output_path}")
        
        try:
            # Setup
            self.setup_temp_directory()
            
            # Validate inputs
            for file_path in input_files:
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {file_path}")
                    return False
                if not file_path.lower().endswith('.pdf'):
                    logger.error(f"Not a PDF file: {file_path}")
                    return False
            
            # Get layout configuration
            if layout not in self.layouts:
                logger.error(f"Unknown layout: {layout}")
                return False
            
            if layout == 'custom':
                if custom_cols <= 0 or custom_rows <= 0:
                    logger.error("Custom layout requires valid cols and rows")
                    return False
                cols, rows = custom_cols, custom_rows
            elif layout == '4up_dup':
                # Special handling for 4-up with duplicate
                cols, rows = 4, 2  # 4 across, 2 down = 8 total positions
            else:
                cols = self.layouts[layout]['cols']
                rows = self.layouts[layout]['rows']
            
            # Get paper size
            if paper_size == 'Custom':
                if custom_width_mm <= 0 or custom_height_mm <= 0:
                    logger.error("Custom paper size requires valid width and height")
                    return False
                page_size = (custom_width_mm * mm, custom_height_mm * mm)
            else:
                if paper_size not in self.paper_sizes:
                    logger.error(f"Unknown paper size: {paper_size}")
                    return False
                page_size = self.paper_sizes[paper_size]
            
            if landscape:
                page_size = (page_size[1], page_size[0])  # Swap for landscape
            
            # Extract all pages as images
            all_images = []
            for pdf_file in input_files:
                images = self.extract_pages_as_images(pdf_file, dpi)
                if not images:
                    logger.error(f"Failed to extract images from {pdf_file}")
                    return False
                all_images.extend(images)
            
            if not all_images:
                logger.error("No images extracted")
                return False
            
            logger.info(f"Total images to impose: {len(all_images)}")
            
            # Create imposed PDF
            success = self._create_imposed_sheet(
                all_images, output_path, cols, rows, page_size, margin_mm * mm, layout
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Imposition failed: {str(e)}")
            return False
        
        finally:
            self.cleanup()
    
    def generate_preview(self, 
                        input_files: List[str],
                        layout: str = '8x2',
                        paper_size: str = 'A4',
                        custom_cols: int = 0,
                        custom_rows: int = 0,
                        custom_width_mm: float = 0,
                        custom_height_mm: float = 0,
                        landscape: bool = True) -> Optional[str]:
        """Generate a preview image of the imposition layout"""
        
        try:
            self.setup_temp_directory()
            
            # Get layout configuration
            if layout == 'custom':
                if custom_cols <= 0 or custom_rows <= 0:
                    return None
                cols, rows = custom_cols, custom_rows
            else:
                if layout not in self.layouts:
                    return None
                cols = self.layouts[layout]['cols']
                rows = self.layouts[layout]['rows']
            
            # Get paper size
            if paper_size == 'Custom':
                if custom_width_mm <= 0 or custom_height_mm <= 0:
                    return None
                page_size = (custom_width_mm * mm, custom_height_mm * mm)
            else:
                if paper_size not in self.paper_sizes:
                    return None
                page_size = self.paper_sizes[paper_size]
            
            if landscape:
                page_size = (page_size[1], page_size[0])
            
            # Extract first few pages as thumbnails
            preview_images = []
            max_preview_pages = min(cols * rows, 16)  # Limit preview pages
            
            for pdf_file in input_files:
                if len(preview_images) >= max_preview_pages:
                    break
                images = self.extract_pages_as_images(pdf_file, dpi=150)  # Lower DPI for preview
                preview_images.extend(images[:max_preview_pages - len(preview_images)])
            
            if not preview_images:
                return None
            
            # Create preview layout
            preview_path = os.path.join(self.temp_dir, "preview.png")
            success = self._create_preview_image(
                preview_images, preview_path, cols, rows, page_size, 5 * mm
            )
            
            return preview_path if success else None
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return None
    
    def _create_preview_image(self, images: List[str], output_path: str,
                            cols: int, rows: int, page_size: Tuple[float, float],
                            margin: float) -> bool:
        """Create preview image using PIL"""
        
        try:
            from PIL import Image, ImageDraw
            
            sheet_width, sheet_height = page_size
            # Convert points to pixels (assuming 72 DPI for preview)
            preview_width = int(sheet_width * 72 / 72)
            preview_height = int(sheet_height * 72 / 72)
            
            # Create preview image
            preview_img = Image.new('RGB', (preview_width, preview_height), 'white')
            draw = ImageDraw.Draw(preview_img)
            
            # Calculate cell dimensions
            available_width = preview_width - (cols + 1) * int(margin * 72 / 72)
            available_height = preview_height - (rows + 1) * int(margin * 72 / 72)
            cell_width = available_width // cols
            cell_height = available_height // rows
            
            # Draw grid
            margin_px = int(margin * 72 / 72)
            for col in range(cols + 1):
                x = margin_px + col * (cell_width + margin_px)
                draw.line([(x, 0), (x, preview_height)], fill='lightgray', width=1)
            
            for row in range(rows + 1):
                y = margin_px + row * (cell_height + margin_px)
                draw.line([(0, y), (preview_width, y)], fill='lightgray', width=1)
            
            # Place thumbnail images
            for i, image_path in enumerate(images[:cols * rows]):
                if not os.path.exists(image_path):
                    continue
                    
                col = i % cols
                row = i // cols
                
                x = margin_px + col * (cell_width + margin_px)
                y = margin_px + row * (cell_height + margin_px)
                
                try:
                    # Load and resize image
                    img = Image.open(image_path)
                    img.thumbnail((cell_width - 4, cell_height - 4), Image.Resampling.LANCZOS)
                    
                    # Center the image in the cell
                    paste_x = x + (cell_width - img.width) // 2
                    paste_y = y + (cell_height - img.height) // 2
                    
                    preview_img.paste(img, (paste_x, paste_y))
                    
                except Exception as e:
                    logger.warning(f"Failed to add image {i+1} to preview: {e}")
                    # Draw placeholder rectangle
                    draw.rectangle([x+2, y+2, x+cell_width-2, y+cell_height-2], 
                                 outline='red', fill='lightpink')
                    draw.text((x+10, y+10), f"Page {i+1}", fill='red')
            
            # Save preview
            preview_img.save(output_path, 'PNG')
            return True
            
        except Exception as e:
            logger.error(f"Preview image creation failed: {e}")
            return False
    
    def _create_imposed_sheet(self, 
                            images: List[str],
                            output_path: str,
                            cols: int,
                            rows: int,
                            page_size: Tuple[float, float],
                            margin: float,
                            layout: str = '') -> bool:
        """Create the actual imposed sheet using the proven method from pdf_impose_single_final.py"""
        
        sheet_width, sheet_height = page_size
        pages_per_sheet = cols * rows
        
        logger.info(f"Sheet dimensions: {sheet_width:.1f} x {sheet_height:.1f} points")
        logger.info(f"Grid: {cols}x{rows} ({pages_per_sheet} pages per sheet)")
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Use the exact method from pdf_impose_single_final.py for 8x2 layout
        if cols == 8 and rows == 2 and layout == '8x2':
            return self._create_8x2_single_sheet_exact(images, output_path, margin)
        elif layout == '4up_dup':
            return self._create_4up_duplicate_sheet(images, output_path, margin)
        else:
            return self._create_general_imposed_sheet(images, output_path, cols, rows, page_size, margin)
    
    def _create_8x2_single_sheet_exact(self, images: List[str], output_path: str, margin: float) -> bool:
        """Create 8x2 layout with exact target dimensions: 460×124mm"""
        
        logger.info("Using exact 8x2 method with target dimensions: 460×124mm")
        
        # Target dimensions: 460×124mm (exactly)
        target_width_mm = 460.0
        target_height_mm = 124.0
        
        sheet_width = target_width_mm * mm
        sheet_height = target_height_mm * mm
        
        cols, rows = 8, 2
        
        # Calculate spacing with extra space for barcode (left) and text (right)
        # Based on reference PDF layout
        
        # Calculate page size to accommodate barcode and text spaces
        # With 8mm barcode + 8mm text = 16mm total extra space needed
        # Balance between image size and barcode/text space
        # 53mm gives good image size while preserving adequate margins
        page_size_mm = 53  # Increased from 50mm for better image visibility
        page_size = page_size_mm * mm
        
        # Calculate required spacing to fit target dimensions
        total_page_width = cols * page_size
        total_page_height = rows * page_size
        
        # Remaining space for margins and gaps
        remaining_width = sheet_width - total_page_width
        remaining_height = sheet_height - total_page_height
        
        # Allocate extra space for barcode (left) and text (right)
        # Based on Affinity Studio inspection - need much more space
        barcode_space_mm = 8.0  # Extra space for barcode on left (increased from 1.5mm)
        text_space_mm = 8.0     # Extra space for text on right (increased from 1.5mm)
        
        barcode_space = barcode_space_mm * mm
        text_space = text_space_mm * mm
        
        # Remaining space after allocating barcode and text areas
        remaining_for_gaps = remaining_width - barcode_space - text_space
        
        # Calculate spacing: left_margin + 7_internal_gaps + right_margin = 9 gaps total
        internal_gap_count = cols - 1  # 7 gaps between 8 pages
        h_spacing = remaining_for_gaps / (internal_gap_count + 2)  # +2 for left/right margins
        
        # Left margin includes barcode space
        left_margin = h_spacing + barcode_space
        # Right margin includes text space  
        right_margin = h_spacing + text_space
        
        # Vertical spacing (unchanged)
        v_spacing = remaining_height / (rows + 1)  # Top margin + gaps + bottom margin
        
        logger.info(f"Target 8x2 dimensions: {sheet_width/mm:.1f} x {sheet_height/mm:.1f} mm")
        logger.info(f"Target 8x2 dimensions: {sheet_width:.1f} x {sheet_height:.1f} points")
        logger.info(f"Page size: {page_size/mm:.1f} x {page_size/mm:.1f} mm")
        logger.info(f"Left margin (with barcode space): {left_margin/mm:.1f}mm")
        logger.info(f"Right margin (with text space): {right_margin/mm:.1f}mm")
        logger.info(f"Internal horizontal spacing: {h_spacing/mm:.1f}mm between images")
        logger.info(f"Vertical spacing: {v_spacing/mm:.1f}mm between images")
        
        # Create PDF with exact dimensions
        c = canvas.Canvas(output_path, pagesize=(sheet_width, sheet_height))
        
        # Place each image with barcode/text spacing
        for i, image_file in enumerate(images[:16]):  # Max 16 images for 8x2
            col = i % cols
            row = i // cols
            
            # Calculate position with barcode space on left, text space on right
            x = left_margin + col * (page_size + h_spacing)
            y = sheet_height - v_spacing - (row + 1) * page_size - row * v_spacing
            
            try:
                # Draw the image with barcode/text spacing
                c.drawImage(image_file, x, y, width=page_size, height=page_size)
                logger.debug(f"Placed image {i+1} at position ({col}, {row}) with barcode/text spacing")
                
            except Exception as e:
                logger.warning(f"Failed to place image {i+1}: {e}")
        
        c.save()
        logger.info(f"✅ Exact 8x2 imposed PDF created: {output_path}")
        return True
    
    def _create_4up_duplicate_sheet(self, images: List[str], output_path: str, margin: float) -> bool:
        """Create 4-up with duplicate layout (4x2 = 8 total copies)"""
        
        logger.info("Creating 4-up with duplicate layout (4x2 = 8 total)")
        
        # Calculate dimensions to match the sample file exactly
        # Sample: 1,326.614 x 805.039 points
        # Work backwards: (1326.614 - 5*5mm) / 4 = page_width
        # (805.039 - 3*5mm) / 2 = page_height
        
        # Use exact dimensions from sample
        sheet_width = 1326.614  # Exact from sample
        sheet_height = 805.039  # Exact from sample
        cols, rows = 4, 2
        margin = 5 * mm
        
        # Calculate page size from sheet dimensions
        page_width = (sheet_width - (cols + 1) * margin) / cols
        page_height = (sheet_height - (rows + 1) * margin) / rows
        page_size = min(page_width, page_height)  # Use square pages
        
        # sheet_width and sheet_height already set above to match sample exactly
        
        logger.info(f"4-up duplicate dimensions: {sheet_width:.1f} x {sheet_height:.1f} points")
        logger.info(f"Expected similar to sample: 1,326.614 x 805.039 points")
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=(sheet_width, sheet_height))
        
        # For 4-up duplicate, we take the first 4 pages and duplicate them
        # Top row: pages 1, 2, 3, 4
        # Bottom row: pages 1, 2, 3, 4 (duplicated)
        
        source_pages = images[:4]  # Take first 4 pages
        if len(source_pages) < 4:
            # If we have fewer than 4 pages, repeat them to fill 4 slots
            while len(source_pages) < 4:
                source_pages.extend(images[:min(4-len(source_pages), len(images))])
        
        # Place 8 images total (4 unique pages, each duplicated)
        for i in range(8):
            col = i % cols
            row = i // cols
            
            # Use the appropriate source page (cycle through first 4)
            source_index = i % 4
            if source_index < len(source_pages):
                image_file = source_pages[source_index]
            else:
                continue  # Skip if no image available
            
            x = margin + col * (page_size + margin)
            y = sheet_height - margin - (row + 1) * page_size
            
            try:
                # Draw the image
                c.drawImage(image_file, x, y, width=page_size, height=page_size)
                logger.debug(f"Placed image {source_index + 1} (copy {i + 1}) at position ({col}, {row})")
                
            except Exception as e:
                logger.warning(f"Failed to place image at position {i + 1}: {e}")
        
        c.save()
        logger.info(f"✅ 4-up duplicate imposed PDF created: {output_path}")
        return True
    
    def _create_general_imposed_sheet(self, images: List[str], output_path: str, 
                                    cols: int, rows: int, page_size: Tuple[float, float], 
                                    margin: float) -> bool:
        """Create general imposed sheet for other layouts"""
        
        sheet_width, sheet_height = page_size
        pages_per_sheet = cols * rows
        
        # Calculate cell dimensions
        available_width = sheet_width - (cols + 1) * margin
        available_height = sheet_height - (rows + 1) * margin
        cell_width = available_width / cols
        cell_height = available_height / rows
        
        logger.info(f"Cell dimensions: {cell_width:.1f} x {cell_height:.1f} points")
        
        # Create PDF
        c = canvas.Canvas(output_path, pagesize=page_size)
        
        # Process images in sheets
        total_sheets = (len(images) + pages_per_sheet - 1) // pages_per_sheet
        
        for sheet_num in range(total_sheets):
            if sheet_num > 0:
                c.showPage()  # New sheet
            
            sheet_start = sheet_num * pages_per_sheet
            logger.info(f"Creating sheet {sheet_num + 1}/{total_sheets}")
            
            # Draw grid lines (optional)
            c.setStrokeColorRGB(0.9, 0.9, 0.9)
            c.setLineWidth(0.5)
            
            # Vertical lines
            for col in range(cols + 1):
                x = margin + col * (cell_width + margin)
                c.line(x, 0, x, sheet_height)
            
            # Horizontal lines  
            for row in range(rows + 1):
                y = margin + row * (cell_height + margin)
                c.line(0, y, sheet_width, y)
            
            # Place images
            for i in range(pages_per_sheet):
                image_index = sheet_start + i
                if image_index >= len(images):
                    break
                
                image_path = images[image_index]
                col = i % cols
                row = i // cols
                
                x = margin + col * (cell_width + margin)
                y = sheet_height - margin - (row + 1) * cell_height
                
                try:
                    c.drawImage(image_path, x, y, 
                              width=cell_width, height=cell_height,
                              preserveAspectRatio=True, anchor='c')
                    
                    logger.debug(f"Placed image {image_index + 1} at grid ({col}, {row})")
                    
                except Exception as e:
                    logger.warning(f"Failed to place image {image_index + 1}: {e}")
        
        c.save()
        logger.info(f"✅ General imposed PDF created: {output_path}")
        return True
    
    def batch_process(self, config_file: str) -> bool:
        """Process multiple jobs from JSON configuration"""
        logger.info(f"Starting batch processing from {config_file}")
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            jobs = config.get('jobs', [])
            success_count = 0
            
            for i, job in enumerate(jobs, 1):
                job_name = job.get('name', f'Job {i}')
                logger.info(f"Processing job {i}/{len(jobs)}: {job_name}")
                
                success = self.create_imposition(
                    input_files=job['input_files'],
                    output_path=job['output_path'],
                    layout=job.get('layout', '8x2'),
                    paper_size=job.get('paper_size', 'A4'),
                    margin_mm=job.get('margin_mm', 5),
                    landscape=job.get('landscape', True),
                    dpi=job.get('dpi', 300)
                )
                
                if success:
                    success_count += 1
                    logger.info(f"✅ Job {i} completed successfully")
                else:
                    logger.error(f"❌ Job {i} failed")
            
            logger.info(f"Batch complete: {success_count}/{len(jobs)} jobs successful")
            return success_count == len(jobs)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            return False
    
    def list_layouts(self):
        """List available layouts"""
        print("\nAvailable Layouts:")
        print("-" * 40)
        for key, layout in self.layouts.items():
            print(f"{key:8} - {layout['description']}")
        print()
    
    def list_paper_sizes(self):
        """List available paper sizes"""
        print("\nAvailable Paper Sizes:")
        print("-" * 40)
        for size in self.paper_sizes.keys():
            print(f"  {size}")
        print()

def create_sample_config():
    """Create sample configuration file"""
    config = {
        "company": "Your Company Name",
        "created": datetime.now().isoformat(),
        "jobs": [
            {
                "name": "Charm 8x2 Layout",
                "input_files": [
                    "samples/Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_1.pdf",
                    "samples/Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_2.pdf"
                ],
                "output_path": "output/charm_8x2_imposed.pdf",
                "layout": "8x2",
                "paper_size": "A4",
                "landscape": True,
                "margin_mm": 5,
                "dpi": 300
            },
            {
                "name": "Standard 4-up Layout",
                "input_files": ["input1.pdf", "input2.pdf"],
                "output_path": "output/standard_4up.pdf",
                "layout": "4up",
                "paper_size": "A3",
                "landscape": True,
                "margin_mm": 10,
                "dpi": 300
            }
        ]
    }
    
    with open('company_imposition_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Sample configuration created: company_imposition_config.json")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Company PDF Imposition Software',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single job
  python company_pdf_imposer.py --input file1.pdf file2.pdf --output result.pdf --layout 8x2

  # Batch processing
  python company_pdf_imposer.py --batch config.json

  # Create sample config
  python company_pdf_imposer.py --create-config
        """
    )
    
    parser.add_argument('--input', nargs='+', help='Input PDF files')
    parser.add_argument('--output', help='Output PDF file')
    parser.add_argument('--layout', default='8x2', help='Layout type (default: 8x2)')
    parser.add_argument('--paper', default='A4', help='Paper size (default: A4)')
    parser.add_argument('--margin', type=float, default=5, help='Margin in mm (default: 5)')
    parser.add_argument('--portrait', action='store_true', help='Use portrait orientation')
    parser.add_argument('--dpi', type=int, default=300, help='Image DPI (default: 300)')
    parser.add_argument('--batch', help='Batch process from JSON config file')
    parser.add_argument('--create-config', action='store_true', help='Create sample config file')
    parser.add_argument('--list-layouts', action='store_true', help='List available layouts')
    parser.add_argument('--list-papers', action='store_true', help='List available paper sizes')
    
    args = parser.parse_args()
    
    imposer = CompanyPDFImposer()
    
    if args.create_config:
        create_sample_config()
        return 0
    
    if args.list_layouts:
        imposer.list_layouts()
        return 0
    
    if args.list_papers:
        imposer.list_paper_sizes()
        return 0
    
    if args.batch:
        success = imposer.batch_process(args.batch)
        return 0 if success else 1
    
    if args.input and args.output:
        success = imposer.create_imposition(
            input_files=args.input,
            output_path=args.output,
            layout=args.layout,
            paper_size=args.paper,
            margin_mm=args.margin,
            landscape=not args.portrait,
            dpi=args.dpi
        )
        return 0 if success else 1
    
    parser.print_help()
    return 1

if __name__ == "__main__":
    sys.exit(main())