"""v2 빌드: html-app/v2/app.html의 <script src="libs/..."> 를 실제 코드로 인라인해
회사망·오프라인에서도 파일 하나로 동작하는 단일 HTML을 만든다.

사용법: python scripts/build_v2.py
출력:  html-app/HS_PDF_TOOL_v2.html
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'html-app' / 'v2' / 'app.html'
OUT = ROOT / 'html-app' / 'HS_PDF_TOOL_v2.html'


def inline_script(match):
    lib_path = ROOT / 'html-app' / 'v2' / match.group(1)
    code = lib_path.read_text(encoding='utf-8')
    # 스크립트 코드 안의 '</script' 가 HTML 파서를 끊지 않게 이스케이프
    # (JS 문자열/정규식 안에서 <\/ 는 </ 와 동일하게 동작)
    code = code.replace('</script', '<\\/script')
    return f'<script>/* === {match.group(1)} === */\n{code}\n</script>'


def main():
    html = SRC.read_text(encoding='utf-8')
    html, n = re.subn(r'<script src="(libs/[^"]+)"></script>', inline_script, html)
    OUT.write_text(html, encoding='utf-8')
    size_mb = OUT.stat().st_size / 1024 / 1024
    print(f"인라인된 라이브러리: {n}개")
    print(f"출력: {OUT} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    main()
