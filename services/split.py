from pypdf import PdfReader, PdfWriter


def parse_page_ranges(range_str, total_pages):
    """Parse page range string like '1-3,5,7-9' into a list of 0-based page indices."""
    pages = []
    for part in range_str.split(','):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-', 1)
            start = int(start.strip())
            end = int(end.strip())
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"잘못된 페이지 범위: {part} (전체 {total_pages}페이지)")
            pages.extend(range(start - 1, end))
        else:
            p = int(part.strip())
            if p < 1 or p > total_pages:
                raise ValueError(f"잘못된 페이지 번호: {p} (전체 {total_pages}페이지)")
            pages.append(p - 1)
    if not pages:
        raise ValueError("추출할 페이지를 지정해주세요.")
    return pages


def split_pdf(input_path, page_range_str, output_path):
    reader = PdfReader(input_path)
    total = len(reader.pages)
    indices = parse_page_ranges(page_range_str, total)

    writer = PdfWriter()
    for idx in indices:
        writer.add_page(reader.pages[idx])
    writer.write(output_path)
    writer.close()
    return output_path, len(indices), total
