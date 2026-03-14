import os
import subprocess
import pikepdf


def compress_lossless(input_path, output_path):
    """Lossless compression using pikepdf: stream recompression, deduplication."""
    with pikepdf.open(input_path) as pdf:
        pdf.save(output_path, recompress_flate=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
    return output_path


def compress_ghostscript(input_path, output_path, setting='/ebook'):
    """Lossy compression using Ghostscript."""
    cmd = [
        'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={setting}',
        '-dNOPAUSE', '-dQUIET', '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"Ghostscript 오류: {result.stderr}")
    return output_path


def compress_pdf(input_path, output_path, level='medium'):
    """Compress PDF at specified quality level.

    level: 'low' (lossless, high quality), 'medium' (/ebook), 'high' (/screen, max compression)
    """
    if level == 'low':
        compress_lossless(input_path, output_path)
    elif level == 'medium':
        compress_ghostscript(input_path, output_path, '/ebook')
    elif level == 'high':
        compress_ghostscript(input_path, output_path, '/screen')
    else:
        raise ValueError(f"알 수 없는 압축 레벨: {level}")

    original_size = os.path.getsize(input_path)
    compressed_size = os.path.getsize(output_path)
    return output_path, original_size, compressed_size
