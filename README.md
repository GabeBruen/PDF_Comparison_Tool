# PDF_Comparison_Tool

**PDF_Comparison_Tool** is a Python tool for comparing PDFs. It converts the first page of each PDF into an image, adds a red border for visual clarity, computes the differences between a known good PDF and a new version, and generates a combined image showing the two originals alongside their differences.

## Features

- **PDF to Image Conversion:** Convert the first page of each PDF to an image using PyMuPDF.
- **Visual Comparison:** Add red borders to images and generate a side-by-side combined image of the good, new, and diff images.
- **Difference Calculation:** Compute a percentage difference between the two images.
- **Flexible Input Options:** Use command-line glob patterns for specifying file sets or select a folder via a GUI.
- **Progress Feedback:** Watch the progress via a command-line progress bar.
- **Robust Error Handling:** Errors during processing are accumulated and reported at the end, with proper exit codes.

## Requirements

- Python 3.x
- [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/) (versions below 1.26 are recommended)
- [Pillow](https://python-pillow.org/)
- [tqdm](https://github.com/tqdm/tqdm)

Usage
Command-Line Mode
You can run the tool by providing two positional glob patterns:
- <glob_pattern_for_good>: Pattern for known good PDF files (e.g., *_good.pdf)
- <glob_pattern_for_new>: Pattern for new PDF files to compare (e.g., *_new.pdf)

Example:
python pdfdiff.py "*_good.pdf" "*_new.pdf"


The tool will process the matching files and create an output_images folder in the same directory as your PDFs, containing:
- new_<original_name>.png
- good_<original_name>.png
- combined_<original_name>.png (side-by-side comparison)

GUI Mode
If you run the script without command-line arguments:
python pdfdiff.py


A folder selection dialog will appear. Select the folder that contains your PDF files. The tool will then use the default patterns (*_good.pdf and *_new.pdf) for processing.
Error Handling
- If the number of good and new PDFs does not match, or the filenames do not correspond after removing the _good or _new suffix, the tool will print an error message and exit with a non-zero code.
- Any conversion or loading errors are recorded and output at the end of processing.

License
This project is licensed under the MIT License.
