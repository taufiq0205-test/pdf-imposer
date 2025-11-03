# Company PDF Imposition Software

Internal tool for PDF imposition before printing. Creates professional layouts with multiple pages arranged on single sheets.

## 🏢 For Internal Company Use Only

All libraries used are open-source and safe for commercial/internal use:
- **PyPDF2** (BSD License)
- **ReportLab** (BSD License) 
- **Pillow** (PIL License)
- **poppler/qpdf/pdftk** (GPL - external tools)

## 🚀 Quick Start

### 1. Installation
```bash
python3 install_company_imposer.py
```

### 2. GUI Interface (Easiest)
```bash
python3 gui_imposer.py
```

### 3. Command Line Interface
```bash
# Basic usage
python3 company_pdf_imposer.py --input file1.pdf file2.pdf --output result.pdf --layout 8x2

# Your current working example
python3 company_pdf_imposer.py --input Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_1.pdf Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_2.pdf --output final_imposed.pdf --layout 8x2
```

## 📋 Available Layouts

| Layout | Description | Grid |
|--------|-------------|------|
| `2up` | 2-up layout | 2×1 |
| `4up` | 4-up layout | 2×2 |
| `8up` | 8-up layout | 4×2 |
| `8x2` | **Your current layout** | 8×2 |
| `16up` | 16-up layout | 4×4 |

## 📄 Paper Sizes

- A4, A3, A2, A1
- Letter, Legal, Tabloid

## 🔧 Features

### ✅ What It Does
- **Single sheet output** - All pages on one sheet (like your example)
- **High-quality image preservation** - 300 DPI extraction
- **Multiple layouts** - 2-up, 4-up, 8x2, 16-up, etc.
- **Batch processing** - Process multiple jobs from config file
- **Professional quality** - Ready for commercial printing
- **Logging** - Full activity logs for troubleshooting

### 🎯 Perfect For
- Print shop preparation
- Booklet creation
- Proof sheets
- Production workflows
- Internal company printing

## 💼 Usage Examples

### GUI Interface
1. Run `python3 gui_imposer.py`
2. Add your PDF files
3. Select layout (8x2 for your case)
4. Choose output location
5. Click "Create Imposed PDF"

### Command Line Examples

```bash
# Your 8x2 layout (8 horizontal, 2 vertical)
python3 company_pdf_imposer.py \
  --input raw_1.pdf raw_2.pdf \
  --output imposed_8x2.pdf \
  --layout 8x2 \
  --paper A4 \
  --margin 5

# 4-up layout on A3 paper
python3 company_pdf_imposer.py \
  --input file1.pdf file2.pdf \
  --output imposed_4up.pdf \
  --layout 4up \
  --paper A3

# Custom settings
python3 company_pdf_imposer.py \
  --input *.pdf \
  --output result.pdf \
  --layout 8x2 \
  --paper A4 \
  --margin 10 \
  --dpi 600 \
  --portrait
```

### Batch Processing

1. Create config file:
```json
{
  "company": "Your Company Name",
  "jobs": [
    {
      "name": "Daily Charm Production",
      "input_files": ["raw_1.pdf", "raw_2.pdf"],
      "output_path": "output/daily_charms.pdf",
      "layout": "8x2",
      "paper_size": "A4",
      "landscape": true,
      "margin_mm": 5,
      "dpi": 300
    }
  ]
}
```

2. Run batch:
```bash
python3 company_pdf_imposer.py --batch production_config.json
```

## 🔍 Command Reference

```bash
# Show help
python3 company_pdf_imposer.py --help

# List available layouts
python3 company_pdf_imposer.py --list-layouts

# List paper sizes
python3 company_pdf_imposer.py --list-papers

# Create sample config
python3 company_pdf_imposer.py --create-config
```

## 📁 File Structure

```
company-pdf-imposer/
├── company_pdf_imposer.py     # Main CLI tool
├── gui_imposer.py             # GUI interface
├── install_company_imposer.py # Installation script
├── sample_config.json         # Sample batch config
├── output/                    # Output directory
├── imposition.log            # Activity log
└── README_Company_PDF_Imposer.md
```

## 🛠️ Technical Details

### Dependencies
- **Python 3.7+**
- **PyPDF2** - PDF manipulation
- **ReportLab** - PDF generation
- **Pillow** - Image processing
- **poppler-utils** - PDF to image conversion
- **qpdf** - PDF utilities

### How It Works
1. **Extract pages** as high-quality images (300 DPI)
2. **Calculate layout** based on paper size and grid
3. **Create canvas** with proper dimensions
4. **Place images** in grid positions
5. **Generate PDF** with all pages on single sheet

### Output Format
- **Single PDF page** containing all input pages
- **Grid layout** as specified (8x2, 4up, etc.)
- **High resolution** suitable for professional printing
- **Proper scaling** to fit grid cells

## 🚨 Troubleshooting

### Common Issues

**"pdftoppm not found"**
```bash
# macOS
brew install poppler

# Linux
sudo apt-get install poppler-utils
```

**"Images not showing"**
- Check input PDF files are valid
- Ensure sufficient disk space
- Check permissions on output directory

**"Layout looks wrong"**
- Verify paper size setting
- Check landscape/portrait orientation
- Adjust margin settings

### Logs
Check `imposition.log` for detailed error messages and processing information.

## 📞 Support

For internal company support:
1. Check the log file: `imposition.log`
2. Verify all dependencies are installed
3. Test with sample files first
4. Contact IT department for system-level issues

## 🔒 Legal & Licensing

✅ **Safe for internal company use**
- All libraries have business-friendly licenses
- No licensing fees or restrictions
- No attribution required in output PDFs
- Suitable for commercial printing workflows

---

**Company PDF Imposition Software** - Internal Tool v1.0