import os
from flask import Blueprint, request, render_template, send_file, jsonify
from services.utils import validate_pdf, save_upload, safe_remove, unique_filename
from services.pdf_to_image import pdf_to_images
from services.pdf_to_ppt import pdf_to_ppt
from config import OUTPUT_FOLDER

convert_bp = Blueprint('convert', __name__)


@convert_bp.route('/pdf-to-image')
def pdf_to_image_page():
    return render_template('pdf_to_image.html')


@convert_bp.route('/pdf-to-ppt')
def pdf_to_ppt_page():
    return render_template('pdf_to_ppt.html')


@convert_bp.route('/api/pdf-to-image', methods=['POST'])
def api_pdf_to_image():
    file = request.files.get('file')
    fmt = request.form.get('format', 'png').strip().lower()
    dpi = int(request.form.get('dpi', '200'))

    if fmt not in ('png', 'jpg', 'jpeg'):
        return jsonify(error="지원하지 않는 이미지 포맷입니다."), 400
    if dpi < 72 or dpi > 600:
        return jsonify(error="DPI는 72~600 사이여야 합니다."), 400

    input_path = None
    zip_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)

        zip_path, page_count = pdf_to_images(input_path, OUTPUT_FOLDER, fmt=fmt, dpi=dpi)

        response = send_file(zip_path, as_attachment=True,
                             download_name=os.path.basename(zip_path),
                             mimetype='application/zip')

        @response.call_on_close
        def cleanup():
            safe_remove(input_path)
            safe_remove(zip_path)

        return response
    except ValueError as e:
        safe_remove(input_path)
        safe_remove(zip_path)
        return jsonify(error=str(e)), 400
    except Exception as e:
        safe_remove(input_path)
        safe_remove(zip_path)
        return jsonify(error=f"변환 중 오류가 발생했습니다: {str(e)}"), 500


@convert_bp.route('/api/pdf-to-ppt', methods=['POST'])
def api_pdf_to_ppt():
    file = request.files.get('file')
    dpi = int(request.form.get('dpi', '200'))

    if dpi < 72 or dpi > 600:
        return jsonify(error="DPI는 72~600 사이여야 합니다."), 400

    input_path = None
    output_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)
        output_path = unique_filename('presentation.pptx', OUTPUT_FOLDER)

        pdf_to_ppt(input_path, output_path, dpi=dpi)

        response = send_file(output_path, as_attachment=True,
                             download_name='presentation.pptx',
                             mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation')

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
        return jsonify(error=f"변환 중 오류가 발생했습니다: {str(e)}"), 500
