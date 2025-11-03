# PDF Imposition Tool

Professional PDF imposition software for creating print-ready layouts. Transform multiple PDF pages into single sheets with customizable grid layouts.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey.svg)

## 🎯 Features

- **Multiple Layout Options**: 2-up, 4-up, 8-up, 8×2, 16-up layouts
- **High-Quality Output**: 300 DPI image extraction preserves visual quality
- **Professional Results**: Single-sheet PDFs ready for commercial printing
- **Flexible Interface**: Both GUI and command-line interfaces
- **Batch Processing**: Handle multiple jobs with JSON configuration
- **Multiple Paper Sizes**: A4, A3, A2, A1, Letter, Legal, Tabloid
- **Cross-Platform**: Works on macOS, Linux, and Windows

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-imposition-tool.git
cd pdf-imposition-tool

# Run the installer
python3 install_company_imposer.py
```

### Basic Usage

#### GUI Interface (Recommended)
```bash
python3 gui_imposer.py
```

#### Command Line
```bash
# Basic 8×2 layout (8 horizontal, 2 vertical)
python3 company_pdf_imposer.py --input file1.pdf file2.pdf --output result.pdf --layout 8x2

# Custom settings
python3 company_pdf_imposer.py \
  --input *.pdf \
  --output imposed.pdf \
  --layout 4up \
  --paper A3 \
  --margin 10 \
  --dpi 600
```

## 📋 Available Layouts

| Layout | Grid | Description | Best For |
|--------|------|-------------|----------|
| `2up` | 2×1 | Two pages side by side | Booklets, brochures |
| `4up` | 2×2 | Four pages in square | Flyers, postcards |
| `8up` | 4×2 | Eight pages in rectangle | Business cards |
| `8x2` | 8×2 | Eight horizontal, two vertical | Stickers, labels |
| `16up` | 4×4 | Sixteen pages in square | Thumbnails, proofs |

## 🖥️ Screenshots

### GUI Interface
The intuitive graphical interface makes PDF imposition accessible to all users:

- Drag-and-drop PDF files
- Visual layout selection
- Real-time preview options
- Progress tracking

### Command Line Interface
Powerful CLI for automation and batch processing:

```bash
# Show available options
python3 company_pdf_imposer.py --help

# List all layouts
python3 company_pdf_imposer.py --list-layouts

# Batch processing
python3 company_pdf_imposer.py --batch production_config.json
```

## 📦 Batch Processing

Create a JSON configuration file for automated workflows:

```json
{
  "company": "Your Company Name",
  "jobs": [
    {
      "name": "Daily Production Run",
      "input_files": ["raw_1.pdf", "raw_2.pdf"],
      "output_path": "output/daily_imposed.pdf",
      "layout": "8x2",
      "paper_size": "A4",
      "landscape": true,
      "margin_mm": 5,
      "dpi": 300
    },
    {
      "name": "Business Cards",
      "input_files": ["business_card.pdf"],
      "output_path": "output/business_cards_8up.pdf",
      "layout": "8up",
      "paper_size": "A4",
      "landscape": false,
      "margin_mm": 10,
      "dpi": 600
    }
  ]
}
```

Run batch processing:
```bash
python3 company_pdf_imposer.py --batch config.json
```

## 🛠️ Technical Details

### Dependencies

**Python Packages:**
- `PyPDF2` - PDF manipulation
- `ReportLab` - PDF generation
- `Pillow` - Image processing
- `tkinter` - GUI interface (built-in)

**System Tools:**
- `poppler-utils` - PDF to image conversion
- `qpdf` - PDF utilities
- `pdftk-java` - PDF toolkit

### How It Works

1. **Extract Pages**: Converts PDF pages to high-quality images (300 DPI)
2. **Calculate Layout**: Determines grid positioning based on paper size
3. **Create Canvas**: Generates properly sized canvas with margins
4. **Place Images**: Positions images in grid cells with aspect ratio preservation
5. **Generate PDF**: Creates single-sheet PDF ready for printing

### Output Quality

- **High Resolution**: 300 DPI default (configurable up to 600 DPI)
- **Aspect Ratio Preserved**: Images maintain original proportions
- **Professional Quality**: Suitable for commercial printing
- **Optimized File Size**: Efficient compression without quality loss

## 📖 Documentation

### Command Line Options

```bash
python3 company_pdf_imposer.py [OPTIONS]

Options:
  --input FILES         Input PDF files (space-separated)
  --output FILE         Output PDF file path
  --layout LAYOUT       Layout type (2up, 4up, 8up, 8x2, 16up)
  --paper SIZE          Paper size (A4, A3, A2, A1, Letter, Legal, Tabloid)
  --margin MM           Margin in millimeters (default: 5)
  --dpi DPI             Image resolution (default: 300)
  --portrait            Use portrait orientation (default: landscape)
  --batch CONFIG        Batch process from JSON config file
  --list-layouts        Show available layouts
  --list-papers         Show available paper sizes
  --create-config       Create sample configuration file
  --help                Show help message
```

### Paper Sizes

| Size | Dimensions (mm) | Dimensions (inches) |
|------|-----------------|-------------------|
| A4 | 210 × 297 | 8.27 × 11.69 |
| A3 | 297 × 420 | 11.69 × 16.54 |
| A2 | 420 × 594 | 16.54 × 23.39 |
| A1 | 594 × 841 | 23.39 × 33.11 |
| Letter | 216 × 279 | 8.5 × 11 |
| Legal | 216 × 356 | 8.5 × 14 |
| Tabloid | 279 × 432 | 11 × 17 |

## 🔧 Installation Details

### Automatic Installation
```bash
python3 install_company_imposer.py
```

### Manual Installation

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install system dependencies
brew install poppler qpdf pdftk-java

# Install Python packages
pip3 install PyPDF2 reportlab pillow
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install poppler-utils qpdf pdftk

# Install Python packages
pip3 install PyPDF2 reportlab pillow
```

#### Windows
1. Download and install [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
2. Download and install [qpdf for Windows](https://github.com/qpdf/qpdf/releases)
3. Add tools to system PATH
4. Install Python packages: `pip install PyPDF2 reportlab pillow`

## 🚨 Troubleshooting

### Common Issues

**"pdftoppm not found"**
```bash
# macOS
brew install poppler

# Linux
sudo apt-get install poppler-utils
```

**"Permission denied" errors**
- Ensure write permissions for output directory
- Check file permissions on input PDFs

**"Images not showing in output"**
- Verify input PDFs contain valid content
- Check available disk space
- Ensure proper DPI settings

**GUI not starting**
- Verify tkinter is installed: `python3 -c "import tkinter"`
- On Linux: `sudo apt-get install python3-tk`

### Logging

All operations are logged to `imposition.log`:
```bash
# View recent logs
tail -f imposition.log

# Search for errors
grep ERROR imposition.log
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/pdf-imposition-tool.git
cd pdf-imposition-tool

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python3 -m pytest tests/
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for all functions
- Include unit tests for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

- **PyPDF2**: BSD License
- **ReportLab**: BSD License  
- **Pillow**: PIL License
- **poppler**: GPL License (external tool)
- **qpdf**: Apache 2.0 License (external tool)

## 🙏 Acknowledgments

- [PyPDF2](https://github.com/py-pdf/PyPDF2) for PDF manipulation
- [ReportLab](https://www.reportlab.com/) for PDF generation
- [Poppler](https://poppler.freedesktop.org/) for PDF rendering
- [qpdf](https://github.com/qpdf/qpdf) for PDF utilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pdf-imposition-tool/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pdf-imposition-tool/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/pdf-imposition-tool/wiki)

---

**Made with ❤️ for the printing industry**