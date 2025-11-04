# Quick Start Guide

## Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install system tools (macOS)
brew install poppler qpdf pdftk-java
```

## Usage

### GUI Mode (Recommended)
```bash
python main.py
```
- Drag and drop PDF files
- Select layout (8x2, 4up, etc.)
- Choose paper size and settings
- Click "Create Imposed PDF"

### CLI Mode
```bash
# Basic usage
python main.py --cli --input file1.pdf file2.pdf --output result.pdf --layout 8x2

# List available layouts
python main.py --cli --list-layouts

# Create sample config
python main.py --cli --create-config

# Batch processing
python main.py --cli --batch config.json
```

### Test with Sample Files
```bash
# Create sample config
python main.py --cli --create-config

# Run with sample files
python main.py --cli --input samples/Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_1.pdf samples/Charm-56x56mm-Sample/CHM2UP_Sample/Raw_PDF/raw_2.pdf --output output/test_8x2.pdf --layout 8x2
```

## Available Layouts
- **2up**: 2×1 grid (booklets, brochures)
- **4up**: 2×2 grid (flyers, postcards)  
- **8up**: 4×2 grid (business cards)
- **8x2**: 8×2 grid (stickers, labels)
- **16up**: 4×4 grid (thumbnails, proofs)
- **4up_dup**: 4×2 grid with duplicates (8 total copies)

## Paper Sizes
A4, A3, A2, A1, Letter, Legal, Tabloid, Custom

## Output
All output files are saved to the `output/` directory by default.