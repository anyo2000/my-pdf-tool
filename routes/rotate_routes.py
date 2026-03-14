from flask import Blueprint, request, render_template, send_file, jsonify
from services.utils import validate_pdf, save_upload, safe_remove, unique_filename
from services.rotate import rotate_pdf
from config import OUTPUT_FOLDER

rotate_bp = Blueprint('rotate', __name__)


@rotate_bp.route('/rotate')
def rotate_page():
    return render_template('rotate.html')


@rotate_bp.route('/api/rotate', methods=['POST'])
def api_rotate():
    file = request.files.get('file')
    pages = request.form.get('pages', 'all').strip()
    angle = int(request.form.get('angle', '90'))

    if angle not in (90, 180, 270):
        return jsonify(error="회전 각도는 90, 180, 270 중 하나여야 합니다."), 400

    input_path = None
    output_path = None
    try:
        validate_pdf(file)
        input_path = save_upload(file)
        output_path = unique_filename('rotated.pdf', OUTPUT_FOLDER)

        rotate_pdf(input_path, output_path, pages=pages, angle=angle)

        response = send_file(output_path, as_attachment=True,
                             download_name='rotated.pdf', mimetype='application/pdf')

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
        return jsonify(error=f"회전 중 오류가 발생했습니다: {str(e)}"), 500
