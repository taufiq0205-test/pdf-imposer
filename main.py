#!/usr/bin/env python3
"""
PDF Imposition Tool - Single Entry Point
Launch GUI by default, or CLI with --cli flag
"""

import sys
import argparse

def main():
    """Main entry point - route to GUI or CLI"""
    
    # Quick check for CLI mode
    if '--cli' in sys.argv:
        # Remove --cli flag and pass remaining args to CLI
        sys.argv.remove('--cli')
        from src.cli.main import main as cli_main
        return cli_main()
    
    # Check for help flags
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return 0
    
    # Default: Launch GUI
    try:
        print("Starting PDF Imposition Tool GUI...")
        from src.gui.main_window import main as gui_main
        return gui_main()
    except ImportError as e:
        print(f"Error: Could not start GUI: {e}")
        print("Try installing required packages: pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"Error starting GUI: {e}")
        return 1

def print_help():
    """Print help information"""
    print("""
PDF Imposition Tool - Professional PDF imposition software

Usage:
  python main.py                    # Launch GUI (default)
  python main.py --cli [options]    # Use command line interface
  python main.py --help             # Show this help

GUI Mode (default):
  - Drag and drop PDF files
  - Visual layout selection
  - Real-time preview
  - Advanced settings

CLI Mode:
  python main.py --cli --input file1.pdf file2.pdf --output result.pdf --layout 8x2
  python main.py --cli --batch config.json
  python main.py --cli --create-config
  python main.py --cli --list-layouts

Available Layouts:
  2up, 4up, 8up, 8x2, 16up, 4up_dup, custom

For detailed CLI help:
  python main.py --cli --help
""")

if __name__ == "__main__":
    sys.exit(main())