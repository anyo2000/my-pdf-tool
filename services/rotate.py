from pypdf import PdfReader, PdfWriter


def rotate_pdf(input_path, output_path, pages="all", angle=90):
    """Rotate specified pages of a PDF.

    pages: 'all' or comma-separated page numbers (1-based)
    angle: 90, 180, or 270
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()
    total = len(reader.pages)

    if pages == "all":
        target_pages = set(range(total))
    else:
        target_pages = set()
        for part in pages.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-', 1)
                for p in range(int(start.strip()) - 1, int(end.strip())):
                    target_pages.add(p)
            else:
                target_pages.add(int(part.strip()) - 1)

    for i in range(total):
        page = reader.pages[i]
        if i in target_pages:
            page.rotate(angle)
        writer.add_page(page)

    writer.write(output_path)
    writer.close()
    return output_path
