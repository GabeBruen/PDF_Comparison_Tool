#!/usr/bin/env python3
__version__ = "1.0.2"

import sys
import argparse  # For command line function.
import glob     # Importing glob for GlobStar Notation
import fitz     # PyMuPDF (Works on latest version.)
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm  # Importing tqdm for the progress bar

import os
# Suppress macOS TK deprecation warnings for NSOpenPanel
os.environ.setdefault('TK_SILENCE_DEPRECATION', '1')


"""
AI code was used as a base to help me get started, but
I added on to the code to make it more user-friendly, both for
the user and anyone looking at this code. -GVB
"""

"""
7/25/25 Added --version command.
Made program easier to use.
Unable to test MacOS fix since I don't have a Mac.
PDF Comparison Tool v 1.0.2
"""

# Global list to accumulate error messages.
error_messages = []


def pdf_to_image(pdf_path, output_path):
    """
    Convert the first page of a PDF to a PNG image.
    """
    global error_messages
    try:
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(0)
        pix = page.get_pixmap()
        pix.save(output_path)
    except Exception as e:
        error_messages.append(f"Error converting PDF '{pdf_path}' to image: {e}")


def load_images(image_path1, image_path2):
    """
    Load two images and return as PIL Image objects.
    """
    global error_messages
    try:
        return Image.open(image_path1), Image.open(image_path2)
    except FileNotFoundError as e:
        error_messages.append(f"File not found: {e.filename}")
    except Exception as e:
        error_messages.append(f"Unexpected error loading images '{image_path1}' and '{image_path2}': {e}")
    return None, None


def add_border(image, border_size=10, color='red'):
    """
    Add a colored border around an image.
    """
    img_with_border = Image.new(
        'RGB',
        (image.width + 2 * border_size, image.height + 2 * border_size),
        color
    )
    img_with_border.paste(image, (border_size, border_size))
    return img_with_border


def calculate_difference(image1, image2):
    """
    Compute the pixel difference and percentage change.
    """
    diff = ImageChops.difference(image1, image2)
    stat = ImageStat.Stat(diff)
    diff_percentage = (sum(stat.mean) / (len(stat.mean) * 255)) * 100
    return diff, round(diff_percentage, 5)


def save_combined_image(image1, image2, diff, output_path):
    """
    Draw borders and concatenate new, good, and diff images side by side.
    """
    img1 = add_border(image1)
    img2 = add_border(image2)
    img_diff = add_border(diff)

    combined = Image.new(
        'RGB',
        (img1.width * 3, img1.height)
    )
    combined.paste(img1, (0, 0))
    combined.paste(img2, (img1.width, 0))
    combined.paste(img_diff, (img1.width * 2, 0))
    combined.save(output_path)


def extract_ids(files, pattern):
    """
    Strip out the constant parts of filenames via glob pattern to match pairs.
    """
    extracted_ids = []
    pattern_base = os.path.basename(pattern)
    for f in files:
        name = os.path.basename(f)
        for part in pattern_base.split('*'):
            if part:
                name = name.replace(part, '')
        extracted_ids.append(name)
    return extracted_ids


def process_pdf_pairs(good_pdfs, new_pdfs, output_folder, progress_bar):
    """
    Convert, compare, and save images for each pair of PDFs.
    """
    for good_pdf, new_pdf in zip(good_pdfs, new_pdfs):
        base = os.path.basename(good_pdf).rsplit('.', 1)[0]
        new_img = os.path.join(output_folder, f"{base}_new.png")
        good_img = os.path.join(output_folder, f"{base}_good.png")
        combined = os.path.join(output_folder, f"{base}_combined.png")

        pdf_to_image(new_pdf, new_img)
        progress_bar.update(0.2)

        pdf_to_image(good_pdf, good_img)
        progress_bar.update(0.2)

        img1, img2 = load_images(new_img, good_img)
        progress_bar.update(0.2)
        if img1 is None or img2 is None:
            continue

        diff, pct = calculate_difference(img1, img2)
        progress_bar.update(0.2)

        tqdm.write(f"Difference for '{base}': {pct:.5f}%")
        save_combined_image(img1, img2, diff, combined)
        progress_bar.update(0.2)


def get_args():
    """
    Parse command-line arguments for patterns and version.
    """
    parser = argparse.ArgumentParser(
        description="PDF Comparison Tool v1.0.2"
    )
    parser.add_argument(
        "good_pattern",
        type=str,
        help="Glob pattern for known good PDFs (e.g., '*_good.pdf')"
    )
    parser.add_argument(
        "new_pattern",
        type=str,
        help="Glob pattern for new PDFs (e.g., '*_new.pdf')"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    return parser.parse_args()


def main():
    global error_messages

    # Determine CLI vs. GUI mode
    if len(sys.argv) > 1:
        args = get_args()
        cwd = os.getcwd()
        good_pattern = os.path.join(cwd, args.good_pattern)
        new_pattern = os.path.join(cwd, args.new_pattern)
    else:
        root = tk.Tk()
        root.withdraw()

        folder = filedialog.askdirectory(title="Select Folder Containing PDFs")
        if not folder:
            sys.stderr.write("Error: No folder selected. Exiting.\n")
            sys.exit(1)

        print("Enter glob pattern for good PDFs (e.g., '*_good.pdf', excluding quotes):")
        good_input = input("> ").strip()
        print("Enter glob pattern for new PDFs (e.g., '*_new.pdf', excluding quotes):")
        new_input = input("> ").strip()

        if not good_input or not new_input:
            sys.stderr.write("Error: Patterns cannot be empty.\n")
            sys.exit(1)

        good_pattern = os.path.join(folder, good_input)
        new_pattern = os.path.join(folder, new_input)

    good_pdfs = sorted(glob.glob(good_pattern))
    new_pdfs = sorted(glob.glob(new_pattern))

    good_ids = extract_ids(good_pdfs, good_pattern)
    new_ids = extract_ids(new_pdfs, new_pattern)
    if sorted(good_ids) != sorted(new_ids):
        sys.stderr.write("Error: Mismatch between extracted file names.\n")
        sys.exit(1)

    out_dir = os.path.join(os.path.dirname(good_pattern), "output_images")
    os.makedirs(out_dir, exist_ok=True)

    total_steps = len(good_pdfs)
    bar_fmt = "{l_bar}{bar} {n}/{total} ({percentage:.1f}%)"
    with tqdm(total=total_steps,
              desc="Processing PDFs",
              bar_format=bar_fmt) as progress_bar:
        process_pdf_pairs(good_pdfs, new_pdfs, out_dir, progress_bar)

    if error_messages:
        tqdm.write("\nErrors occurred during processing:")
        for msg in error_messages:
            tqdm.write(msg)
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
