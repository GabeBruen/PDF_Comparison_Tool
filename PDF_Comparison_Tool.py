#!/usr/bin/env python3

# import statements
import os
import sys
import glob  # Importing glob for GlobStar Notation
import argparse  # Command line functions.
import fitz  # PyMuPDF (Works on latest version.)
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm  # Importing tqdm for the progress bar

"""
AI code was used as a base to help me get started, but
I added on to the code to make it more user-friendly, both for
the user and anyone looking at this code. -GVB
"""

"""
5/2/25 Progress bar works fine on command line, but looks messy in GUI.
Program works with the latest version of PyMuPDF.
PDF Comparison Tool v 1.0
"""

"""
This comment was made by AI -GVB
PDF Diff – A tool for comparing PDFs

This script converts the first page of each PDF into an image, adds a red border, computes the difference,
and creates a combined image for side-by-side comparison.

Usage:
  Command-line mode (preferred):
    python pdfdiff.py "<glob_pattern_for_good>" "<glob_pattern_for_new>"
  Example:
    python pdfdiff.py "*_good.pdf" "*_new.pdf"

  If no patterns are provided, a folder selection GUI will appear (using tkinter), and by default it will
  look for files ending with _good.pdf and _new.pdf.

Ensure that Python is in your PATH and run the script with the desired patterns.
"""

# When using the command line,
# you can specify the folder containing the PDFs to compare using the --folder argument,
# like this:
# python script_name.py --folder /path/to/pdf_folder

# Python must be in your PATH.
# Program must be run in admin mode.

# Global list to accumulate error messages.
error_messages = []


# This turns the PDFs to images.
def pdf_to_image(pdf_path, output_path):
    global error_messages
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(0)  # Get the first page
        pix = page.get_pixmap()
        pix.save(output_path)
    except Exception as e:
        error_messages.append(f"Error converting PDF '{pdf_path}' to image: {e}")


# This loads the newly created images.
def load_images(image_path1, image_path2):
    global error_messages
    try:
        image1 = Image.open(image_path1)
        image2 = Image.open(image_path2)
        return image1, image2
    except FileNotFoundError as e:
        error_messages.append(f"File not found: {e.filename}")
    except Exception as e:
        error_messages.append(f"Unexpected error loading images '{image_path1}' and '{image_path2}': {e}")
    return None, None


# This adds a red border to the image.
def add_border(image, border_size=10, color='red'):
    img_with_border = Image.new('RGB', (image.width + 2 * border_size, image.height + 2 * border_size), color)
    img_with_border.paste(image, (border_size, border_size))
    return img_with_border


# This calculates the differences between the 2 images.
def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)
    stat = ImageStat.Stat(diff)
    diff_percentage = (sum(stat.mean) / (len(stat.mean) * 255)) * 100  # percentage change
    return diff, diff_percentage


# This is for the saved combined image at the end.
def save_combined_image(image1, image2, diff, output_path):
    image1_with_border = add_border(image1)
    image2_with_border = add_border(image2)
    diff_with_border = add_border(diff)

    combined = Image.new('RGB', (image1_with_border.width * 3, image1_with_border.height))
    combined.paste(image1_with_border, (0, 0))
    combined.paste(image2_with_border, (image1_with_border.width, 0))
    combined.paste(diff_with_border, (image1_with_border.width * 2, 0))
    combined.save(output_path)


def main(good_pattern=None, new_pattern=None):
    global error_messages

    if not good_pattern or not new_pattern:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        folder_path = filedialog.askdirectory(title="Select the folder containing PDFs")
        if not folder_path:
            sys.stderr.write("No folder selected. Exiting.\n")
            sys.exit(1)
        good_pattern = os.path.join(folder_path, "*_good.pdf")
        new_pattern = os.path.join(folder_path, "*_new.pdf")

    good_pdfs = sorted(glob.glob(good_pattern))
    new_pdfs = sorted(glob.glob(new_pattern))

    if len(good_pdfs) != len(new_pdfs):
        sys.stderr.write("Error: The number of good and new PDFs do not match.\n")
        sys.exit(1)

    good_ids = [os.path.basename(f).replace("_good.pdf", "") for f in good_pdfs]
    new_ids = [os.path.basename(f).replace("_new.pdf", "") for f in new_pdfs]
    if sorted(good_ids) != sorted(new_ids):
        sys.stderr.write("Error: Mismatch between good and new PDF filenames.\n")
        sys.exit(1)

    output_folder = os.path.join(os.path.dirname(good_pdfs[0]) if good_pdfs else ".", "output_images")
    os.makedirs(output_folder, exist_ok=True)

    # Set up a single progress bar for the entire process
    total_steps = len(good_pdfs) * 5  # Each file pair has 5 operations
    with tqdm(total=total_steps, desc="Processing PDFs", ncols=80, leave=True) as progress_bar:
        for good_pdf, new_pdf in zip(good_pdfs, new_pdfs):
            new_image_path = os.path.join(output_folder, f"new_{os.path.basename(new_pdf)}.png")
            good_image_path = os.path.join(output_folder, f"good_{os.path.basename(good_pdf)}.png")
            combined_image_path = os.path.join(output_folder, f"combined_{os.path.basename(good_pdf)}.png")

            # Convert PDFs to images
            pdf_to_image(new_pdf, new_image_path)
            progress_bar.update(1)
            pdf_to_image(good_pdf, good_image_path)
            progress_bar.update(1)

            # Load images
            image1, image2 = load_images(new_image_path, good_image_path)
            progress_bar.update(1)

            if image1 is None or image2 is None:
                continue

            # Calculate the difference
            diff, diff_percentage = calculate_difference(image1, image2)
            progress_bar.update(1)

            # **Display the difference percentage below the progress bar**
            tqdm.write(f"Difference percentage for {os.path.basename(new_pdf)}: {diff_percentage:.2f}%")

            # Save the combined comparison image
            save_combined_image(image1, image2, diff, combined_image_path)
            progress_bar.update(1)

    # Display errors at the end (if any)
    if error_messages:
        tqdm.write("\nErrors occurred during processing:")
        for msg in error_messages:
            tqdm.write(msg)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    # This block ensures that the script runs only when it is executed directly,
    # and not when it is imported as a module in another Python file.

    parser = argparse.ArgumentParser(description="PDF Comparator Tool")
    # Creates an argument parser to handle command-line arguments.
    # 'description' explains what the script does, and appears in the help message.

    parser.add_argument(
        "good_pattern",
        nargs="?",
        help='Glob pattern for the known good PDFs (e.g., "*_good.pdf")'
    )
    # Adds the first positional argument "good_pattern".
    # This argument specifies a pattern (GlobStar notation) to locate the known good PDF files.

    parser.add_argument(
        "new_pattern",
        nargs="?",
        help='Glob pattern for the new PDFs to compare (e.g., "*_new.pdf")'
    )
    # Adds the second positional argument "new_pattern".
    # This argument specifies a pattern (GlobStar notation) to locate the new PDF files for comparison.

    args = parser.parse_args()
    # Parses the command-line arguments provided by the user.
    # The results are stored in the "args" object.

    main(good_pattern=args.good_pattern, new_pattern=args.new_pattern)
    # Calls the 'main' function, passing in the parsed glob patterns as arguments.
    # This initiates the program's functionality using the provided inputs.
