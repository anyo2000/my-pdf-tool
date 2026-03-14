import os
from flask import Blueprint, request, render_template, send_file, jsonify
from services.utils import validate_pdf, save_upload, safe_remove, unique_filename
from services.compress import compress_pdf
from config import OUTPUT_FOLDER

compress_bp = Blueprint('compress', __name__)


@compress_bp.route('/compress')
def compress_page():
    return render_template('compress.html')


@compress_bp.route('/api/compress', methods=['POST'])
def api_compress():
    file = request.files.get('file')
    level = request.form.get('level', 'medium').strip()

    if level not in ('low', 'medium', 'high'):
        return jsonify(error="잘못된 압축 레벨입니다."), 400

    input_path = None
    output_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)
        output_path = unique_filename('compressed.pdf', OUTPUT_FOLDER)

        _, original_size, compressed_size = compress_pdf(input_path, output_path, level)
        ratio = round((1 - compressed_size / original_size) * 100, 1) if original_size > 0 else 0

        response = send_file(output_path, as_attachment=True,
                             download_name='compressed.pdf', mimetype='application/pdf')
        response.headers['X-Original-Size'] = str(original_size)
        response.headers['X-Compressed-Size'] = str(compressed_size)
        response.headers['X-Compression-Ratio'] = str(ratio)
        response.headers['Access-Control-Expose-Headers'] = 'X-Original-Size, X-Compressed-Size, X-Compression-Ratio'

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
        return jsonify(error=f"압축 중 오류가 발생했습니다: {str(e)}"), 500
