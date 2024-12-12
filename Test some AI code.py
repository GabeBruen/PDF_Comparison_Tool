# latexpdfdiff

import subprocess
import os
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog

# This turns the PDFs to images.
def pdf_to_image(pdf_path, output_folder, output_name):
    try:
        # Ensure the paths are correctly formatted with double quotes
        pdf_path = f'"{os.path.abspath(pdf_path)}"'
        output_path = f'"{os.path.join(output_folder, output_name)}.png"'
        # Converts to a PNG
        result = subprocess.run(['convert', pdf_path, output_path], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error converting PDF to image: {e.stderr}")

# This loads the newly created images.
def load_images(image_path1, image_path2):
    # Loads first image
    image1 = Image.open(image_path1)  # Pillow
    # Loads second image
    image2 = Image.open(image_path2)  # Pillow
    return image1, image2

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

def ask_for_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory()  # Open the file explorer to select a folder
    return folder_path

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

# Prompt to ask for a folder path
print("Where do you want to put your newly created images?")
selected_folder = ask_for_folder()

# This converts the PDFs to images. (Calls first function.)
pdf_to_image(test_pdf, selected_folder, 'test')
pdf_to_image(good_pdf, selected_folder, 'good')

# This loads the images. (Calls second function.)
image1, image2 = load_images(os.path.join(selected_folder, 'test.png'), os.path.join(selected_folder, 'good.png'))

# This will calculate the difference between the 2 images. (Calls third function.)
diff, diff_percentage = calculate_difference(image1, image2)

# This prints the calculated difference
print(f"Difference percentage: {diff_percentage:.2f}%")

# This saves the final image. (Calls fourth function.)
save_combined_image(image1, image2, diff, os.path.join(selected_folder, 'combined.png'))