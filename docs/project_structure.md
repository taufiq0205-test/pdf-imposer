# Project Structure

## Overview
The PDF Imposition Tool is organized into a clean, modular structure with a single entry point.

## Directory Structure

```
pdf-imposition-tool/
├── main.py                     # Single entry point (GUI by default, --cli for CLI)
├── src/                        # Source code
│   ├── __init__.py
│   ├── core/                   # Core imposition logic
│   │   ├── __init__.py
│   │   └── imposer.py          # Main CompanyPDFImposer class
│   ├── gui/                    # GUI components
│   │   ├── __init__.py
│   │   └── main_window.py      # Enhanced GUI interface
│   └── cli/                    # Command line interface
│       ├── __init__.py
│       └── main.py             # CLI implementation
├── samples/                    # Sample files for testing
│   └── Charm-56x56mm-Sample/   # Sample charm layouts
├── output/                     # Default output directory
├── tests/                      # Unit tests (future)
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
├── config.cfg                  # Configuration file
├── README.md                   # Main documentation
└── LICENSE                     # License file
```

## Entry Points

### Single Entry Point: `main.py`
- **Default**: Launches GUI interface
- **With `--cli`**: Launches command line interface
- **With `--help`**: Shows usage information

### Usage Examples
```bash
# Launch GUI (default)
python main.py

# Use CLI
python main.py --cli --input file1.pdf file2.pdf --output result.pdf

# Show help
python main.py --help
```

## Core Components

### `src/core/imposer.py`
- Main `CompanyPDFImposer` class
- All imposition logic and layouts
- PDF processing and image extraction
- Batch processing capabilities

### `src/gui/main_window.py`
- Enhanced GUI with preview
- Real-time layout updates
- Advanced settings
- Progress tracking

### `src/cli/main.py`
- Command line interface
- Argument parsing
- Batch processing support

## Benefits of This Structure

1. **Single Entry Point**: Users only need to remember `python main.py`
2. **Clean Separation**: GUI, CLI, and core logic are separated
3. **Modular**: Easy to maintain and extend
4. **Professional**: Follows Python packaging best practices
5. **Scalable**: Easy to add new features or interfaces

## Migration from Old Structure

Old files have been consolidated:
- `gui_imposer.py` → `src/gui/main_window.py` (enhanced version)
- `company_pdf_imposer.py` → `src/core/imposer.py`
- `enhanced_gui.py` → `src/gui/main_window.py`
- Multiple CLI scripts → `src/cli/main.py`
- Shell scripts → `main.py` (Python entry point)