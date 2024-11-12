# latexpdfdiff

# This import is for the Magick Software stuff.
import subprocess

# This import is for pillow
from PIL import Image, ImageChops, ImageStat

# This import is to get the path to the PDFs
import tkinter as tk
from tkinter import filedialog

# This turns the PDFs to images.
def pdf_to_image(pdf_path, output_folder, output_name):

    # converts to a png
    subprocess.run(['convert', pdf_path, f"{output_folder}/{output_name}.png"])

# This loads the newly created images.
def load_images(image_path1, image_path2):

    # loads first image
    image1 = Image.open(image_path1)  # pillow

    # loads second image
    image2 = Image.open(image_path2)  # pillow

    return image1, image2

# This calculates the differences between the 2 images.
def calculate_difference(image1, image2):

    diff = ImageChops.difference(image1, image2)  # pillow

    stat = ImageStat.Stat(diff)  # pillow

    diff_percentage = sum(stat.mean) / (len(stat.mean) * 255) * 100

    return diff, diff_percentage

# This is for the saved combined image at the end.
def save_combined_image(image1, image2, diff, output_path):

    combined = Image.new('RGB', (image1.width * 3, image1.height))  # pillow

    combined.paste(image1, (0, 0))

    combined.paste(image2, (image1.width, 0))

    combined.paste(diff, (image1.width * 2, 0))

    combined.save(output_path)

# from import tkinter
root = tk.Tk()
root.withdraw()  # Hide the root window

# These bring up the explorer so that user can pick PDFs
# for the test pdf
test_pdf = filedialog.askopenfilename()
# for the known good pdf
good_pdf = filedialog.askopenfilename()

print("Make sure you click the PDF you want to test before inputting a known "
      "good PDF.")

# This converts the PDFs to images. (Calls first function.)
pdf_to_image(test_pdf, 'output', 'test')
pdf_to_image(good_pdf, 'output', 'good')

# In case user didn't put in their PDFs.
if test_pdf == None or good_pdf == None:
    print("Next time, add your PDFs.")
    exit()

# This loads the images. (Calls second function.)
image1, image2 = load_images(test_pdf, good_pdf)

# This will calculate the difference between the 2 images. (Calls third function.)
diff, diff_percentage = calculate_difference(image1, image2)

# this prints the calculated difference
print(f"Difference percentage: {diff_percentage:.2f}%")

# This saves the final image. (Calls fourth function.)
save_combined_image(image1, image2, diff, 'output/combined.png')
