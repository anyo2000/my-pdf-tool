from flask import Flask
from config import MAX_CONTENT_LENGTH
from services.utils import ensure_dirs, start_cleanup_thread


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

    ensure_dirs()

    from routes.merge_routes import merge_bp
    from routes.split_routes import split_bp
    from routes.rotate_routes import rotate_bp
    from routes.compress_routes import compress_bp
    from routes.convert_routes import convert_bp
    from routes.ocr_routes import ocr_bp

    app.register_blueprint(merge_bp)
    app.register_blueprint(split_bp)
    app.register_blueprint(rotate_bp)
    app.register_blueprint(compress_bp)
    app.register_blueprint(convert_bp)
    app.register_blueprint(ocr_bp)

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    start_cleanup_thread()
    app.run(debug=True, port=5000)
