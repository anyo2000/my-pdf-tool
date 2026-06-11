"""NotebookLM 워터마크 제거 스크립트 (프로토타입).

NotebookLM 산출물(PDF/PPTX)은 페이지/슬라이드 전체가 통이미지 1장이고,
우하단 고정 위치에 'NotebookLM' 워터마크가 픽셀로 구워져 있다.
→ 각 행마다 워터마크 박스 왼쪽의 배경색을 샘플링해 덮는 방식으로 제거.

사용법:
  python remove_nblm_watermark.py <입력파일.pdf|.pptx> [출력파일]
"""
from __future__ import annotations

import io
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

import img2pdf
import numpy as np
from PIL import Image

# 워터마크 박스 (1376x768 기준, 여유 마진 포함)
WM_BOX = (1262, 741, 1372, 764)  # x0, y0, x1, y1
BASE_W, BASE_H = 1376, 768


def patch_watermark(img: Image.Image) -> Image.Image:
    """이미지 우하단 워터마크 영역을 행별 좌측 배경색으로 덮는다."""
    arr = np.array(img.convert('RGB'))
    h, w = arr.shape[:2]
    sx, sy = w / BASE_W, h / BASE_H
    x0, y0, x1, y1 = (int(WM_BOX[0] * sx), int(WM_BOX[1] * sy),
                      min(int(WM_BOX[2] * sx) + 1, w), min(int(WM_BOX[3] * sy) + 1, h))
    # 각 행마다 박스 바로 왼쪽 30px의 중앙값으로 채움 (수평 그라데이션·줄무늬 유지)
    sample_x0 = max(0, x0 - 40)
    sample_x1 = max(1, x0 - 10)
    for y in range(y0, y1):
        row_sample = arr[y, sample_x0:sample_x1]
        arr[y, x0:x1] = np.median(row_sample, axis=0).astype(np.uint8)
    return Image.fromarray(arr)


def process_pdf(src: str, dst: str) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        # 원본이 72dpi 통이미지(1376x768)라 72dpi 렌더 = 원본 픽셀 1:1
        subprocess.run(['pdftoppm', '-png', '-r', '72', src, os.path.join(tmp, 'p')],
                       check=True, timeout=300)
        pages = sorted(f for f in os.listdir(tmp) if f.endswith('.png'))
        out_paths = []
        for name in pages:
            path = os.path.join(tmp, name)
            patched = patch_watermark(Image.open(path))
            patched.save(path)
            out_paths.append(path)
        with open(dst, 'wb') as f:
            f.write(img2pdf.convert(out_paths))
        return len(pages)


def process_pptx(src: str, dst: str) -> int:
    count = 0
    with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith('ppt/media/') and item.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(io.BytesIO(data))
                patched = patch_watermark(img)
                buf = io.BytesIO()
                patched.save(buf, format='PNG' if item.filename.lower().endswith('.png') else 'JPEG')
                data = buf.getvalue()
                count += 1
            zout.writestr(item, data)
    return count


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    base, ext = os.path.splitext(src)
    dst = sys.argv[2] if len(sys.argv) > 2 else f"{base}_워터마크제거{ext}"
    if ext.lower() == '.pdf':
        n = process_pdf(src, dst)
        print(f"완료: {n}페이지 처리 → {dst}")
    elif ext.lower() == '.pptx':
        n = process_pptx(src, dst)
        print(f"완료: 이미지 {n}장 처리 → {dst}")
    else:
        print(f"지원하지 않는 형식: {ext}")
        sys.exit(1)


if __name__ == '__main__':
    main()
