import os
from flask import Blueprint, request, render_template, send_file, jsonify
from services.utils import validate_pdf, save_upload, safe_remove, unique_filename
from services.merge import merge_pdfs
from config import OUTPUT_FOLDER

merge_bp = Blueprint('merge', __name__)


@merge_bp.route('/merge')
def merge_page():
    return render_template('merge.html')


@merge_bp.route('/api/merge', methods=['POST'])
def api_merge():
    files = request.files.getlist('files')
    if len(files) < 2:
        return jsonify(error="2개 이상의 PDF 파일을 업로드해주세요."), 400

    saved_paths = []
    try:
        for f in files:
            validate_pdf(f)
            saved_paths.append(save_upload(f))

        output_path = unique_filename('merged.pdf', OUTPUT_FOLDER)
        merge_pdfs(saved_paths, output_path)

        response = send_file(output_path, as_attachment=True,
                             download_name='merged.pdf', mimetype='application/pdf')

        @response.call_on_close
        def cleanup():
            for p in saved_paths:
                safe_remove(p)
            safe_remove(output_path)

        return response
    except ValueError as e:
        for p in saved_paths:
            safe_remove(p)
        return jsonify(error=str(e)), 400
    except Exception as e:
        for p in saved_paths:
            safe_remove(p)
        return jsonify(error=f"병합 중 오류가 발생했습니다: {str(e)}"), 500
