from pdf2image import convert_from_path
import pytesseract


def ocr_pdf(input_path, lang='kor+eng', dpi=300):
    """Extract text from PDF pages using OCR.

    lang: tesseract language code(s), e.g. 'kor', 'eng', 'kor+eng'
    """
    images = convert_from_path(input_path, dpi=dpi)
    results = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img, lang=lang)
        results.append({
            'page': i + 1,
            'text': text.strip()
        })
    full_text = '\n\n'.join(
        f"--- 페이지 {r['page']} ---\n{r['text']}" for r in results
    )
    return full_text, len(images)
