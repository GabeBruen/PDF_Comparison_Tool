# import statements
import os
import sys
import argparse  # For command line function.
import glob  # Importing glob for GlobStar Notation
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
5/17/25 Program more precise with decimals.
Output images look better.
Progress bar still looks messy in GUI.
Command line portion not tested.
PDF Comparison Tool v 1.0.1
"""

# When using the command line,
# you can specify the folder containing the PDFs to compare using the --folder argument,
# like this:
# python script_name.py --folder /path/to/pdf_folder

# Python must be in your PATH.

# Global list to accumulate error messages.
error_messages = []


# Function to convert PDFs to images.
def pdf_to_image(pdf_path, output_path):
    global error_messages
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(0)  # Get the first page
        pix = page.get_pixmap()
        pix.save(output_path)
    except Exception as e:
        error_messages.append(f"Error converting PDF '{pdf_path}' to image: {e}")


# Function to load images for comparison.
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


# Function to add a red border to images.
def add_border(image, border_size=10, color='red'):
    img_with_border = Image.new('RGB', (image.width + 2 * border_size, image.height + 2 * border_size), color)
    img_with_border.paste(image, (border_size, border_size))
    return img_with_border


# Function to calculate differences between two images.
def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)
    stat = ImageStat.Stat(diff)
    diff_percentage = (sum(stat.mean) / (len(stat.mean) * 255)) * 100  # Percentage change

    # Increased decimal precision for better differentiation.
    return diff, round(diff_percentage, 5)


# Function to save the combined comparison image.
def save_combined_image(image1, image2, diff, output_path):
    image1_with_border = add_border(image1)
    image2_with_border = add_border(image2)
    diff_with_border = add_border(diff)

    combined = Image.new('RGB', (image1_with_border.width * 3, image1_with_border.height))
    combined.paste(image1_with_border, (0, 0))
    combined.paste(image2_with_border, (image1_with_border.width, 0))
    combined.paste(diff_with_border, (image1_with_border.width * 2, 0))
    combined.save(output_path)


# Improved function to extract IDs dynamically based on glob patterns.
def extract_ids(files, pattern):
    extracted_ids = []
    pattern_base = os.path.basename(pattern)

    for f in files:
        f_basename = os.path.basename(f)
        for part in pattern_base.split('*'):
            if part:
                f_basename = f_basename.replace(part, '')
        extracted_ids.append(f_basename)

    return extracted_ids


# Main processing function.
def process_pdf_pairs(good_pdfs, new_pdfs, output_folder, progress_bar):
    for good_pdf, new_pdf in zip(good_pdfs, new_pdfs):
        base_name = os.path.basename(good_pdf).split('.')[0]  # Standardized naming
        new_image_path = os.path.join(output_folder, f"{base_name}_new.png")
        good_image_path = os.path.join(output_folder, f"{base_name}_good.png")
        combined_image_path = os.path.join(output_folder, f"{base_name}_combined.png")

        # Convert PDFs to images.
        pdf_to_image(new_pdf, new_image_path)
        progress_bar.update(0.2)
        pdf_to_image(good_pdf, good_image_path)
        progress_bar.update(0.2)

        # Load images.
        image1, image2 = load_images(new_image_path, good_image_path)
        progress_bar.update(0.2)

        if image1 is None or image2 is None:
            continue

        # Calculate the difference.
        diff, diff_percentage = calculate_difference(image1, image2)
        progress_bar.update(0.2)

        tqdm.write(f"Difference percentage for {base_name}: {diff_percentage:.5f}%")  # More decimal places.

        # Save the combined comparison image.
        save_combined_image(image1, image2, diff, combined_image_path)
        progress_bar.update(0.2)


def get_args():
    """Parse command-line arguments for glob patterns."""
    parser = argparse.ArgumentParser(description="PDF Comparison Tool v1.0.1")
    parser.add_argument("good_pattern", type=str, help="Glob pattern for known good PDFs (e.g., '*_good.pdf')")
    parser.add_argument("new_pattern", type=str, help="Glob pattern for new PDFs to compare (e.g., '*_new.pdf')")
    args = parser.parse_args()
    return args


def main():
    global error_messages

    # Check if command-line patterns are provided
    if len(sys.argv) > 1:
        args = get_args()
        folder_path = os.getcwd()  # Assume current directory
        good_pattern = os.path.join(folder_path, args.good_pattern)
        new_pattern = os.path.join(folder_path, args.new_pattern)
    else:
        # GUI fallback
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select Folder Containing PDFs")

        if not folder_path:
            sys.stderr.write("Error: No folder selected. Exiting.\n")
            sys.exit(1)

        print("Enter the glob pattern for the known good PDFs (e.g., '*_good.pdf'):")
        good_pattern = input("> ").strip()
        print("Enter the glob pattern for the new PDFs to compare (e.g., '*_new.pdf'):")
        new_pattern = input("> ").strip()

        if not good_pattern or not new_pattern:
            sys.stderr.write("Error: Patterns cannot be empty.\n")
            sys.exit(1)

        good_pattern = os.path.join(folder_path, good_pattern)
        new_pattern = os.path.join(folder_path, new_pattern)

    # Get file lists
    good_pdfs = sorted(glob.glob(good_pattern))
    new_pdfs = sorted(glob.glob(new_pattern))

    # Ensure matching filenames
    good_ids = extract_ids(good_pdfs, good_pattern)
    new_ids = extract_ids(new_pdfs, new_pattern)

    if sorted(good_ids) != sorted(new_ids):
        sys.stderr.write("Error: Mismatch between extracted file IDs.\n")
        sys.exit(1)

    output_folder = os.path.join(folder_path, "output_images")
    os.makedirs(output_folder, exist_ok=True)

    total_steps = len(good_pdfs)
    with tqdm(total=total_steps, desc="Processing PDFs", ncols=80, leave=True) as progress_bar:
        process_pdf_pairs(good_pdfs, new_pdfs, output_folder, progress_bar)

    # Display errors at the end
    if error_messages:
        tqdm.write("\nErrors occurred during processing:")
        for msg in error_messages:
            tqdm.write(msg)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
