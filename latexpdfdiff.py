# import statements
import os
import fitz  # PyMuPDF (Using a version higher than 1.25.1 will break the program.)
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm  # Importing tqdm for the progress bar
import glob  # Importing glob for GlobStar Notation
import argparse

# latexpdfdiff

"""
AI code was used as a base to help me get started, but
I added on to the code to make it more user-friendly, both for
the user and anyone looking at this code. -GVB
"""

"""
3/10/25 Except for command line, everything has been tested.
"""

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
        print(f"\nConverted {pdf_path} to {output_path}")
        if progress_bar:
            progress_bar.update(1)  # Update progress bar
    except Exception as e:
        print(f"\nError converting PDF to image: {e}")


# This loads the newly created images.
def load_images(image_path1, image_path2, progress_bar=None):
    try:
        image1 = Image.open(image_path1)  # Pillow
        image2 = Image.open(image_path2)  # Pillow
        if progress_bar:
            progress_bar.update(1)  # Update progress bar
        return image1, image2
    except FileNotFoundError as e:
        print(f"\nFile not found: {e.filename}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")


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
        print("GlobStar notation works if the files are formatted like this...")
        print("'*_new.pdf' '*_good.pdf'")
        # This brings up the explorer so that user can pick the folder containing PDFs
        folder_path = filedialog.askdirectory(title="Select the folder containing PDFs")

        # In case user didn't select the folder.
        if not folder_path:
            print("Next time, add your PDFs folder.")
            exit()

    # Define the output folder for the images
    output_folder = os.path.join(folder_path, 'output_images')
    os.makedirs(output_folder, exist_ok=True)

    # Find all new and good PDFs using GlobStar Notation
    new_pdfs = glob.glob(os.path.join(folder_path, '*_new.pdf'))
    good_pdfs = glob.glob(os.path.join(folder_path, '*_good.pdf'))

    # Ensure we have the same number of new and good PDFs
    if len(new_pdfs) != len(good_pdfs):
        print("The number of new and good PDFs do not match.")
        exit()

    # Initialize the progress bar
    total_steps = len(new_pdfs) * 4
    progress_bar = tqdm(total=total_steps, desc='Processing')

    for new_pdf, good_pdf in zip(new_pdfs, good_pdfs):
        print(f"\nProcessing pair: {new_pdf}, {good_pdf}")

        # Define the output paths for the images
        new_image_path = os.path.join(output_folder, f'new_{os.path.basename(new_pdf)}.png')
        good_image_path = os.path.join(output_folder, f'good_{os.path.basename(good_pdf)}.png')
        combined_image_path = os.path.join(output_folder, f'combined_{os.path.basename(new_pdf)}.png')

        # This converts the PDFs to images. (Calls first function.)
        pdf_to_image(new_pdf, new_image_path, progress_bar)
        pdf_to_image(good_pdf, good_image_path, progress_bar)

        # This loads the images. (Calls second function.)
        image1, image2 = load_images(new_image_path, good_image_path, progress_bar)
        if image1 is None or image2 is None:
            print(f"\nFailed to load images for: {new_pdf}, {good_pdf}")
            continue  # Skip this pair

        # This will calculate the difference between the 2 images. (Calls third function.)
        diff, diff_percentage = calculate_difference(image1, image2)
        progress_bar.update(1)  # Update progress bar

        # This prints the calculated difference
        print(f"\nDifference percentage for {os.path.basename(new_pdf)}: {diff_percentage:.2f}%")

        # This saves the final image. (Calls fourth function.)
        save_combined_image(image1, image2, diff, combined_image_path)
        progress_bar.update(1)  # Update progress bar

    progress_bar.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Comparator")
    parser.add_argument("--folder", help="Folder containing the PDFs to compare")
    args = parser.parse_args()

    if args.folder:
        main(folder_path=args.folder)
    else:
        main()
