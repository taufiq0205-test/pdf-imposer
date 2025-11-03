#!/usr/bin/env python3
"""
Installation script for Company PDF Imposition Software
Sets up all dependencies and creates shortcuts
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_python_packages():
    """Install required Python packages"""
    packages = [
        'PyPDF2',
        'reportlab',
        'pillow'
    ]
    
    print("\n📦 Installing Python packages...")
    for package in packages:
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def install_system_tools():
    """Install system tools based on platform"""
    system = platform.system().lower()
    
    print(f"\n🔧 Installing system tools for {system}...")
    
    if system == 'darwin':  # macOS
        tools = ['poppler', 'qpdf', 'pdftk-java']
        for tool in tools:
            try:
                result = subprocess.run(['brew', 'list', tool], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {tool} already installed")
                else:
                    print(f"📥 Installing {tool}...")
                    subprocess.run(['brew', 'install', tool], check=True)
                    print(f"✅ {tool} installed")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {tool}")
                return False
            except FileNotFoundError:
                print("❌ Homebrew not found. Please install Homebrew first:")
                print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
                return False
    
    elif system == 'linux':
        tools = ['poppler-utils', 'qpdf', 'pdftk']
        try:
            for tool in tools:
                print(f"📥 Installing {tool}...")
                subprocess.run(['sudo', 'apt-get', 'install', '-y', tool], check=True)
                print(f"✅ {tool} installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install system tools")
            print("Please install manually: sudo apt-get install poppler-utils qpdf pdftk")
            return False
    
    elif system == 'windows':
        print("⚠️  Windows detected. Please install manually:")
        print("   1. Download poppler for Windows")
        print("   2. Download qpdf for Windows") 
        print("   3. Add to PATH")
        return True
    
    return True

def test_installation():
    """Test if all components are working"""
    print("\n🧪 Testing installation...")
    
    # Test Python imports
    try:
        import PyPDF2
        import reportlab
        from PIL import Image
        print("✅ Python packages working")
    except ImportError as e:
        print(f"❌ Python package test failed: {e}")
        return False
    
    # Test system tools
    tools = ['pdftoppm', 'qpdf']
    for tool in tools:
        try:
            subprocess.run([tool, '--help'], capture_output=True, check=True)
            print(f"✅ {tool} working")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {tool} not found or not working")
            return False
    
    return True

def create_sample_files():
    """Create sample configuration and test files"""
    print("\n📄 Creating sample files...")
    
    # Create sample config
    sample_config = {
        "company": "Your Company Name",
        "jobs": [
            {
                "name": "Sample 8x2 Layout",
                "input_files": ["sample1.pdf", "sample2.pdf"],
                "output_path": "output/sample_imposed.pdf",
                "layout": "8x2",
                "paper_size": "A4",
                "landscape": True,
                "margin_mm": 5,
                "dpi": 300
            }
        ]
    }
    
    import json
    with open('sample_config.json', 'w') as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ sample_config.json created")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    print("✅ output directory created")

def create_shortcuts():
    """Create desktop shortcuts or scripts"""
    print("\n🔗 Creating shortcuts...")
    
    # Create batch file for Windows or shell script for Unix
    if platform.system().lower() == 'windows':
        script_content = f"""@echo off
cd /d "{os.getcwd()}"
python gui_imposer.py
pause
"""
        with open('Company_PDF_Imposer.bat', 'w') as f:
            f.write(script_content)
        print("✅ Company_PDF_Imposer.bat created")
    
    else:
        script_content = f"""#!/bin/bash
cd "{os.getcwd()}"
python3 gui_imposer.py
"""
        with open('Company_PDF_Imposer.sh', 'w') as f:
            f.write(script_content)
        os.chmod('Company_PDF_Imposer.sh', 0o755)
        print("✅ Company_PDF_Imposer.sh created")

def main():
    """Main installation function"""
    print("🏢 Company PDF Imposition Software Installer")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install Python packages
    if not install_python_packages():
        print("\n❌ Installation failed at Python packages")
        return 1
    
    # Install system tools
    if not install_system_tools():
        print("\n❌ Installation failed at system tools")
        return 1
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed")
        return 1
    
    # Create sample files
    create_sample_files()
    
    # Create shortcuts
    create_shortcuts()
    
    print("\n" + "=" * 50)
    print("✅ Installation completed successfully!")
    print("\n📋 Usage:")
    print("  Command line: python3 company_pdf_imposer.py --help")
    print("  GUI:         python3 gui_imposer.py")
    print("  Batch:       python3 company_pdf_imposer.py --batch sample_config.json")
    
    if platform.system().lower() != 'windows':
        print("  Quick start: ./Company_PDF_Imposer.sh")
    else:
        print("  Quick start: Company_PDF_Imposer.bat")
    
    print("\n📁 Files created:")
    print("  - company_pdf_imposer.py (main CLI tool)")
    print("  - gui_imposer.py (GUI interface)")
    print("  - sample_config.json (sample configuration)")
    print("  - output/ (output directory)")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())