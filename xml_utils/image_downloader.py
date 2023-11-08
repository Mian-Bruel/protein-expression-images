import os
import zipfile

import requests


def download_images(image_urls):
    # Ensure there's a directory to save the images
    os.makedirs("images", exist_ok=True)

    # List to hold the file paths of downloaded images
    image_files = []

    # Download each image
    for i, url in enumerate(image_urls, start=1):
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for request errors

        # Get the image file name from the URL or create one if it doesn't exist
        image_file_name = url.split("/")[-1] or f"image_{i}.jpg"
        image_file_path = os.path.join("images", image_file_name)

        # Save the image to the local directory
        with open(image_file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    file.flush()
                    os.fsync(file.fileno())

        image_files.append(image_file_path)

    return image_files


def zip_images(image_files):
    # Create a zip file containing all images
    zip_file_path = "images.zip"
    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        for file in image_files:
            zipf.write(file, arcname=os.path.basename(file))

    return zip_file_path
