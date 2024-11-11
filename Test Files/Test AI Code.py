# pip install pdf2image pillow

import subprocess

# imports 1 thing from pdf2image
from pdf2image import convert_from_path  # pdf2image

# imports 3 things from pillow
from PIL import Image, ImageChops, ImageStat  # pillow

# This is for dialog for the file
import tkinter as tk
from tkinter import filedialog

def pdf_to_image(pdf_path, output_folder, output_name):
    images = convert_from_path(pdf_path)  # pdf2image
    for i, image in enumerate(images):
        image.save(f"{output_folder}/{output_name}_{i}.png", 'PNG')

def load_images(image_path1, image_path2):
    image1 = Image.open(image_path1)  # pillow
    image2 = Image.open(image_path2)  # pillow
    return image1, image2

def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)  # pillow
    stat = ImageStat.Stat(diff)  # pillow
    diff_percentage = sum(stat.mean) / (len(stat.mean) * 255) * 100
    return diff, diff_percentage

def save_combined_image(image1, image2, diff, output_path):
    combined = Image.new('RGB', (image1.width * 3, image1.height))  # pillow
    combined.paste(image1, (0, 0))  # pillow
    combined.paste(image2, (image1.width, 0))  # pillow
    combined.paste(diff, (image1.width * 2, 0))  # pillow
    combined.save(output_path)  # pillow

root = tk.Tk()
root.withdraw()  # Hide the root window

# Paths to your PDFs
test_pdf = filedialog.askopenfilename()
good_pdf = filedialog.askopenfilename()

# Convert PDFs to images
pdf_to_image(test_pdf, 'output', 'test')  # pdf2image
pdf_to_image(good_pdf, 'output', 'good')  # pdf2image

# Load images
image1, image2 = load_images('output/test_0.png', 'output/good_0.png')  # pillow

# Calculate difference
diff, diff_percentage = calculate_difference(image1, image2)  # pillow
print(f"Difference percentage: {diff_percentage:.2f}%")

# Save combined image
save_combined_image(image1, image2, diff, 'output/combined.png')  # pillow
