from flask import Blueprint, request, render_template, jsonify
from services.utils import validate_pdf, save_upload, safe_remove
from services.ocr import ocr_pdf

ocr_bp = Blueprint('ocr', __name__)


@ocr_bp.route('/ocr')
def ocr_page():
    return render_template('ocr.html')


@ocr_bp.route('/api/ocr', methods=['POST'])
def api_ocr():
    file = request.files.get('file')
    lang = request.form.get('lang', 'kor+eng').strip()

    allowed_langs = {'kor', 'eng', 'kor+eng'}
    if lang not in allowed_langs:
        return jsonify(error="지원하지 않는 언어입니다."), 400

    input_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)

        text, page_count = ocr_pdf(input_path, lang=lang)

        return jsonify(text=text, pages=page_count)
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"OCR 처리 중 오류가 발생했습니다: {str(e)}"), 500
    finally:
        safe_remove(input_path)
