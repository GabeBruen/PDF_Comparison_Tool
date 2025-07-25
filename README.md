```markdown
# PDF_Comparison_Tool

PDF_Comparison_Tool is a Python utility for comparing PDFs. It converts the first page of each PDF into an image, adds a red border for visual clarity, computes the pixel-wise difference between a known good PDF and a new version, and generates a combined image showing the two originals alongside their diffs.

Current Version: v1.0.2

---

## Features

- PDF to Image Conversion: convert the first page of each PDF to PNG using PyMuPDF  
- Visual Comparison: add red borders and generate a side-by-side image of the good, new, and diff outputs  
- Difference Calculation: compute a percentage difference between the two images  
- Flexible Input: accept command-line glob patterns or, in GUI mode, select a folder and enter patterns interactively  
- Progress Feedback: display a simple progress bar showing completed count and percentage  
- Error Reporting: collect and report any conversion/loading errors at the end, with appropriate exit codes  

---

## Requirements

- Python 3.x  
- PyMuPDF  
- Pillow  
- tqdm  

---

## Usage

### Command-Line Mode

Run the tool with two positional glob patterns:

```sh
python PDF_Comparison_Tool.py [--version] "<good_pattern>" "<new_pattern>"
```

- `--version`  
  Show the program version and exit.  
- `<good_pattern>`  
  Glob for known good PDFs (e.g., `'*_good.pdf'`)  
- `<new_pattern>`  
  Glob for new PDFs to compare (e.g., `'*_new.pdf'`)  

Example:

```sh
python PDF_Comparison_Tool.py '*_good.pdf' '*_new.pdf'
```

The tool will process matching files and create an `output_images` folder next to your PDFs, containing:

- `<base>_new.png`  
- `<base>_good.png`  
- `<base>_combined.png` (side-by-side comparison)

Due note: The files you're comparing must be in the same location as PDF_Comparison_Tool.py in Command-Line Mode.

### GUI Mode

If you run the script without any arguments:

```sh
python PDF_Comparison_Tool.py
```

- A folder-selection dialog appears (on macOS, deprecation warnings are suppressed automatically).  
- After picking a folder, you’ll be prompted to enter two glob patterns:  
  1. Pattern for good PDFs (e.g., `*_good.pdf`)  
  2. Pattern for new PDFs (e.g., `*_new.pdf`)  
- The same `output_images` folder—and naming conventions—apply as in command-line mode.

---

## Progress Feedback

The progress bar displays:

- A simple ratio (`n/total`)  
- A percentage complete  

---

## Error Handling

- If the count or IDs of good vs. new PDFs don’t match, the tool exits with an error.  
- Any conversion or I/O errors are listed at the end, and the process returns a non-zero exit code.

---

## License

This project is licensed under the MIT License.
```
