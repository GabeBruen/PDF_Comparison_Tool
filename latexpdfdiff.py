# latexpdfdiff

"""
AI code was used as a base to help me get started, but
I added on to the code to make it more userfriendly, both for
the user and anyone looking at this code. -GVB
"""

"""
2/27/25 Added command line interface option, comparing multiple PDFs
using GlobStarNotation, a progress bar, and red border on separate page.
Added features have not been tested yet.
"""

import os
import sys
import fitz  # PyMuPDF (Using a version higher than 1.25.1 will break the program.)
from PIL import Image, ImageChops, ImageStat, ImageDraw
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm  # Importing tqdm for the progress bar
import glob  # Importing glob for GlobStar Notation
import argparse

# When using the command line,
# you can specify the folder containing the PDFs to compare using the --folder argument,
# like this:
# python script_name.py --folder /path/to/pdf_folder

# This turns the PDFs to images.
def pdf_to_image(pdf_path, output_path, progress_bar=None):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        # Get the first page
        page = pdf_document.load_page(0)
        # Render the page to an image
        pix = page.get_pixmap()
        # Save the image
        pix.save(output_path)
        print(f"Converted {pdf_path} to {output_path}")
        if progress_bar:
            progress_bar.update(1)  # Update progress bar
    except Exception as e:
        print(f"Error converting PDF to image: {e}")

# This loads the newly created images.
def load_images(image_path1, image_path2):
    try:
        image1 = Image.open(image_path1)  # Pillow
        image2 = Image.open(image_path2)  # Pillow
        return image1, image2
    except FileNotFoundError as e:
        print(f"File not found: {e.filename}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# This adds a red border to the image.
def add_border(image, border_size=10, color='red'):
    img_with_border = Image.new('RGB', (image.width + 2 * border_size, image.height + 2 * border_size), color)
    img_with_border.paste(image, (border_size, border_size))
    return img_with_border

# This calculates the differences between the 2 images.
def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)  # Pillow
    stat = ImageStat.Stat(diff)  # Pillow
    diff_percentage = sum(stat.mean) / (len(stat.mean) * 255) * 100
    return diff, diff_percentage

# This is for the saved combined image at the end.
def save_combined_image(image1, image2, diff, output_path):
    image1_with_border = add_border(image1)
    image2_with_border = add_border(image2)
    diff_with_border = add_border(diff)

    combined = Image.new('RGB', (image1_with_border.width * 3, image1_with_border.height))  # Pillow
    combined.paste(image1_with_border, (0, 0))
    combined.paste(image2_with_border, (image1_with_border.width, 0))
    combined.paste(diff_with_border, (image1_with_border.width * 2, 0))
    combined.save(output_path)

def main(folder_path=None):
    if folder_path is None:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        print("Make sure you click the PDF folder you want to test.")
        # This brings up the explorer so that user can pick the folder containing PDFs
        folder_path = filedialog.askdirectory(title="Select the folder containing PDFs")

        # In case user didn't select the folder.
        if not folder_path:
            print("Next time, add your PDFs folder.")
            exit()

    # Define the output folder for the images
    output_folder = os.path.join(folder_path, 'output_images')
    os.makedirs(output_folder, exist_ok=True)

    # Find all test and good PDFs using GlobStar Notation
    test_pdfs = glob.glob(os.path.join(folder_path, 'test_*.pdf'))
    good_pdfs = glob.glob(os.path.join(folder_path, 'good_*.pdf'))

    # Ensure we have the same number of test and good PDFs
    if len(test_pdfs) != len(good_pdfs):
        print("The number of test and good PDFs do not match.")
        exit()

    # Initialize the progress bar
    with tqdm(total=len(test_pdfs) * 4, desc='Processing') as progress_bar:
        for test_pdf, good_pdf in zip(test_pdfs, good_pdfs):
            # Define the output paths for the images
            test_image_path = os.path.join(output_folder, f'test_{os.path.basename(test_pdf)}.png')
            good_image_path = os.path.join(output_folder, f'good_{os.path.basename(good_pdf)}.png')
            combined_image_path = os.path.join(output_folder, f'combined_{os.path.basename(test_pdf)}.png')

            # This converts the PDFs to images. (Calls first function.)
            pdf_to_image(test_pdf, test_image_path, progress_bar)
            pdf_to_image(good_pdf, good_image_path, progress_bar)

            # This loads the images. (Calls second function.)
            image1, image2 = load_images(test_image_path, good_image_path)
            progress_bar.update(1)  # Update progress bar

            # This will calculate the difference between the 2 images. (Calls third function.)
            diff, diff_percentage = calculate_difference(image1, image2)
            progress_bar.update(1)  # Update progress bar

            # This prints the calculated difference
            print(f"Difference percentage for {os.path.basename(test_pdf)}: {diff_percentage:.2f}%")

            # This saves the final image. (Calls fourth function.)
            save_combined_image(image1, image2, diff, combined_image_path)
            progress_bar.update(1)  # Update progress bar

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Comparator")
    parser.add_argument("--folder", help="Folder containing the PDFs to compare")
    args = parser.parse_args()

    if args.folder:
        main(folder_path=args.folder)
    else:
        main()
