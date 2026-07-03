"""pdf.js 폰트 데이터 내장 파일 생성기.

pdf.js는 폰트가 PDF에 내장되지 않은 문서(한글 HWP 인쇄물, 관공서 PDF 등)를
그릴 때 cMap·표준폰트 데이터 파일이 필요하다. file:// 로 여는 단일 HTML에서는
외부 파일을 fetch할 수 없으므로, 데이터를 base64로 담은 JS 파일을 만들어
<script>로 싣는다. (script 태그는 file:// 에서도 로드됨)

사용법: python scripts/gen_pdf_assets.py
출력:  html-app/v2/libs/pdf-assets.js  (커밋 대상 — 재생성은 이 스크립트로)

pdfjs-dist 버전은 libs/pdf.min.js 와 반드시 맞출 것.
"""
import base64
import io
import json
import tarfile
import urllib.request
from pathlib import Path

PDFJS_VERSION = '3.11.174'
TARBALL_URL = f'https://registry.npmjs.org/pdfjs-dist/-/pdfjs-dist-{PDFJS_VERSION}.tgz'

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'html-app' / 'v2' / 'libs' / 'pdf-assets.js'
CACHE = ROOT / 'scripts' / '.cache' / f'pdfjs-dist-{PDFJS_VERSION}.tgz'


def get_tarball():
    if CACHE.exists():
        return CACHE.read_bytes()
    print(f'다운로드: {TARBALL_URL}')
    data = urllib.request.urlopen(TARBALL_URL).read()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(data)
    return data


def main():
    tar = tarfile.open(fileobj=io.BytesIO(get_tarball()))
    cmaps, fonts = {}, {}
    for m in tar.getmembers():
        if not m.isfile():
            continue
        if m.name.startswith('package/cmaps/') and m.name.endswith('.bcmap'):
            name = Path(m.name).stem  # 확장자 없이 CMap 이름 그대로
            cmaps[name] = base64.b64encode(tar.extractfile(m).read()).decode()
        elif m.name.startswith('package/standard_fonts/') and m.name.endswith(('.pfb', '.ttf')):
            fonts[Path(m.name).name] = base64.b64encode(tar.extractfile(m).read()).decode()

    js = (
        f'/* 자동 생성 — scripts/gen_pdf_assets.py (pdfjs-dist {PDFJS_VERSION}) */\n'
        '// 비내장 폰트 렌더용 cMap(.bcmap)·표준폰트 데이터. app.html의 openPdf()가 사용.\n'
        'window.PDF_ASSETS = {\n'
        f'cmaps: {json.dumps(cmaps)},\n'
        f'fonts: {json.dumps(fonts)}\n'
        '};\n'
    )
    OUT.write_text(js, encoding='utf-8')
    print(f'cMap {len(cmaps)}개, 표준폰트 {len(fonts)}개')
    print(f'출력: {OUT} ({OUT.stat().st_size / 1024 / 1024:.1f} MB)')


if __name__ == '__main__':
    main()
