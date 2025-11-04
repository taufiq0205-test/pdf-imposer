#!/usr/bin/env python3
"""
Command Line Interface for PDF Imposition Tool
"""

import sys
import os
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.core.imposer import CompanyPDFImposer, create_sample_config

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='PDF Imposition Tool - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single job
  python main.py --cli --input file1.pdf file2.pdf --output result.pdf --layout 8x2

  # Batch processing
  python main.py --cli --batch config.json

  # Create sample config
  python main.py --cli --create-config
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