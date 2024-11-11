import subprocess
from PIL import Image, ImageChops, ImageStat
import tkinter as tk
from tkinter import filedialog

def pdf_to_image(pdf_path, output_folder, output_name):
    subprocess.run(['convert', pdf_path, f"{output_folder}/{output_name}.png"])

def load_images(image_path1, image_path2):
    image1 = Image.open(image_path1)
    image2 = Image.open(image_path2)
    return image1, image2

def calculate_difference(image1, image2):
    diff = ImageChops.difference(image1, image2)
    stat = ImageStat.Stat(diff)
    diff_percentage = sum(stat.mean) / (len(stat.mean) * 255) * 100
    return diff, diff_percentage

def save_combined_image(image1, image2, diff, output_path):
    combined = Image.new('RGB', (image1.width * 3, image1.height))
    combined.paste(image1, (0, 0))
    combined.paste(image2, (image1.width, 0))
    combined.paste(diff, (image1.width * 2, 0))
    combined.save(output_path)

root = tk.Tk()
root.withdraw()  # Hide the root window

# Paths to your PDFs
test_pdf = filedialog.askopenfilename()
good_pdf = filedialog.askopenfilename()

# Convert PDFs to images
pdf_to_image(test_pdf, 'output', 'test')
pdf_to_image(good_pdf, 'output', 'good')

# Load images
image1, image2 = load_images(test_pdf, good_pdf)

# Calculate difference
diff, diff_percentage = calculate_difference(image1, image2)
print(f"Difference percentage: {diff_percentage:.2f}%")

# Save combined image
save_combined_image(image1, image2, diff, 'output/combined.png')
