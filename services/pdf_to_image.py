import os
import zipfile
from pdf2image import convert_from_path


def pdf_to_images(input_path, output_dir, fmt='png', dpi=200):
    """Convert PDF pages to images, return a zip file path."""
    images = convert_from_path(input_path, dpi=dpi)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    zip_path = os.path.join(output_dir, f"{base_name}_images.zip")

    image_paths = []
    for i, img in enumerate(images):
        ext = fmt.lower()
        img_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.{ext}")
        if ext == 'jpg' or ext == 'jpeg':
            img.save(img_path, 'JPEG', quality=95)
        else:
            img.save(img_path, 'PNG')
        image_paths.append(img_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in image_paths:
            zf.write(p, os.path.basename(p))

    # Clean up individual images
    for p in image_paths:
        os.remove(p)

    return zip_path, len(images)
