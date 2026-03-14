from pypdf import PdfWriter


def merge_pdfs(input_paths, output_path):
    writer = PdfWriter()
    for path in input_paths:
        writer.append(path)
    writer.write(output_path)
    writer.close()
    return output_path
