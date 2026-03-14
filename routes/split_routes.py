from flask import Blueprint, request, render_template, send_file, jsonify
from services.utils import validate_pdf, save_upload, safe_remove, unique_filename
from services.split import split_pdf
from config import OUTPUT_FOLDER

split_bp = Blueprint('split', __name__)


@split_bp.route('/split')
def split_page():
    return render_template('split.html')


@split_bp.route('/api/split', methods=['POST'])
def api_split():
    file = request.files.get('file')
    page_range = request.form.get('pages', '').strip()

    if not page_range:
        return jsonify(error="페이지 범위를 입력해주세요."), 400

    input_path = None
    output_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)
        output_path = unique_filename('split.pdf', OUTPUT_FOLDER)

        _, extracted, total = split_pdf(input_path, page_range, output_path)

        response = send_file(output_path, as_attachment=True,
                             download_name='split.pdf', mimetype='application/pdf')

        @response.call_on_close
        def cleanup():
            safe_remove(input_path)
            safe_remove(output_path)

        return response
    except ValueError as e:
        safe_remove(input_path)
        safe_remove(output_path)
        return jsonify(error=str(e)), 400
    except Exception as e:
        safe_remove(input_path)
        safe_remove(output_path)
        return jsonify(error=f"분할 중 오류가 발생했습니다: {str(e)}"), 500
