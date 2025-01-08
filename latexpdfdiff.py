# latexpdfdiff

"""
AI code was used as a base to help me get started, but
I added on to the code to make it more user friendly, both for
the user and anyone looking at this code. -GVB
"""

import os
import fitz  # PyMuPDF
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog

# This turns the PDFs to images.
def pdf_to_image(pdf_path, output_path):
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


# This calculates the differences between the 2 images.
def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)  # Pillow
    stat = ImageStat.Stat(diff)  # Pillow
    diff_percentage = sum(stat.mean) / (len(stat.mean) * 255) * 100
    return diff, diff_percentage


# This is for the saved combined image at the end.
def save_combined_image(image1, image2, diff, output_path):
    combined = Image.new('RGB', (image1.width * 3, image1.height))  # Pillow
    combined.paste(image1, (0, 0))
    combined.paste(image2, (image1.width, 0))
    combined.paste(diff, (image1.width * 2, 0))
    combined.save(output_path)


# Main script
root = tk.Tk()
root.withdraw()  # Hide the root window

print("Make sure you click the PDF you want to test before inputting a known good PDF.")

# These bring up the explorer so that user can pick PDFs
test_pdf = filedialog.askopenfilename(title="Select the test PDF")
good_pdf = filedialog.askopenfilename(title="Select the known good PDF")

# In case user didn't put in their PDFs.
if not test_pdf or not good_pdf:
    print("Next time, add your PDFs.")
    exit()

# Define the output paths for the images
test_image_path = os.path.join(os.path.dirname(test_pdf), 'test.png')
good_image_path = os.path.join(os.path.dirname(good_pdf), 'good.png')
combined_image_path = os.path.join(os.path.dirname(test_pdf), 'combined.png')

# This converts the PDFs to images. (Calls first function.)
pdf_to_image(test_pdf, test_image_path)
pdf_to_image(good_pdf, good_image_path)

# This loads the images. (Calls second function.)
image1, image2 = load_images(test_image_path, good_image_path)

# This will calculate the difference between the 2 images. (Calls third function.)
diff, diff_percentage = calculate_difference(image1, image2)

# This prints the calculated difference
print(f"Difference percentage: {diff_percentage:.2f}%")

# This saves the final image. (Calls fourth function.)
save_combined_image(image1, image2, diff, combined_image_path)
