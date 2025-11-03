#!/usr/bin/env python3
"""
Company PDF Imposition Software
Internal tool for PDF imposition before printing
Supports multiple layouts and batch processing
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
            '8up': {'cols': 4, 'rows': 2, 'description': '8-up (4x2)'},
            '8x2': {'cols': 8, 'rows': 2, 'description': '8x2 (8 horizontal, 2 vertical)'},
            '16up': {'cols': 4, 'rows': 4, 'description': '16-up (4x4)'},
        }
        
        self.paper_sizes = {
            'A4': A4,
            'A3': A3, 
            'A2': A2,
            'A1': A1,
            'Letter': (8.5*inch, 11*inch),
            'Legal': (8.5*inch, 14*inch),
            'Tabloid': (11*inch, 17*inch)
        }
        
        self.temp_dir = None
    
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
                         dpi: int = 300) -> bool:
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
            
            cols = self.layouts[layout]['cols']
            rows = self.layouts[layout]['rows']
            
            # Get paper size
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
                all_images, output_path, cols, rows, page_size, margin_mm * mm
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Imposition failed: {str(e)}")
            return False
        
        finally:
            self.cleanup()
    
    def _create_imposed_sheet(self, 
                            images: List[str],
                            output_path: str,
                            cols: int,
                            rows: int,
                            page_size: Tuple[float, float],
                            margin: float) -> bool:
        """Create the actual imposed sheet"""
        
        sheet_width, sheet_height = page_size
        pages_per_sheet = cols * rows
        
        # Calculate cell dimensions
        available_width = sheet_width - (cols + 1) * margin
        available_height = sheet_height - (rows + 1) * margin
        cell_width = available_width / cols
        cell_height = available_height / rows
        
        logger.info(f"Sheet dimensions: {sheet_width:.1f} x {sheet_height:.1f} points")
        logger.info(f"Cell dimensions: {cell_width:.1f} x {cell_height:.1f} points")
        logger.info(f"Grid: {cols}x{rows} ({pages_per_sheet} pages per sheet)")
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
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
        logger.info(f"✅ Imposed PDF created: {output_path}")
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
                    "Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_1.pdf",
                    "Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_2.pdf"
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