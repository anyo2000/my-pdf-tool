/* ===== PDF Tool - Shared JS ===== */

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

/* ===== Upload Zone Setup ===== */
function setupUploadZone(zoneId, inputId, opts = {}) {
    const zone = document.getElementById(zoneId);
    const input = document.getElementById(inputId);
    if (!zone || !input) return;

    const multiple = opts.multiple || false;
    const onFiles = opts.onFiles || function() {};

    zone.addEventListener('click', () => input.click());

    zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    });

    zone.addEventListener('dragleave', () => {
        zone.classList.remove('dragover');
    });

    zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files).filter(f => f.name.toLowerCase().endsWith('.pdf'));
        if (files.length === 0) {
            showError('PDF 파일만 업로드할 수 있습니다.');
            return;
        }
        if (!multiple) files.splice(1);
        onFiles(files);
    });

    input.addEventListener('change', () => {
        const files = Array.from(input.files);
        if (files.length > 0) onFiles(files);
        input.value = '';
    });
}

/* ===== File List (for merge) ===== */
function createFileList(containerId, files) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    files.forEach((file, idx) => {
        const item = document.createElement('div');
        item.className = 'file-item';
        item.draggable = true;
        item.dataset.index = idx;

        item.innerHTML = `
            <span class="file-item-name">${file.name}</span>
            <span class="file-item-size">${formatFileSize(file.size)}</span>
            <button class="file-item-remove" data-index="${idx}">&times;</button>
        `;
        container.appendChild(item);
    });

    // Drag-and-drop reorder
    let dragIdx = null;
    container.addEventListener('dragstart', (e) => {
        const item = e.target.closest('.file-item');
        if (!item) return;
        dragIdx = parseInt(item.dataset.index);
        item.classList.add('dragging');
    });

    container.addEventListener('dragend', (e) => {
        const item = e.target.closest('.file-item');
        if (item) item.classList.remove('dragging');
    });

    container.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    container.addEventListener('drop', (e) => {
        e.preventDefault();
        const target = e.target.closest('.file-item');
        if (!target || dragIdx === null) return;
        const dropIdx = parseInt(target.dataset.index);
        if (dragIdx === dropIdx) return;

        const moved = files.splice(dragIdx, 1)[0];
        files.splice(dropIdx, 0, moved);
        createFileList(containerId, files);
        if (window._onFileListChange) window._onFileListChange(files);
    });

    // Remove button
    container.addEventListener('click', (e) => {
        const btn = e.target.closest('.file-item-remove');
        if (!btn) return;
        const removeIdx = parseInt(btn.dataset.index);
        files.splice(removeIdx, 1);
        createFileList(containerId, files);
        if (window._onFileListChange) window._onFileListChange(files);
    });
}

/* ===== XHR Upload with Progress ===== */
function uploadFiles(url, formData, opts = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const progressWrap = document.querySelector('.progress-wrap');
        const progressBar = document.querySelector('.progress-bar-inner');
        const progressText = document.querySelector('.progress-text');

        if (progressWrap) {
            progressWrap.classList.add('active');
        }

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const pct = Math.round((e.loaded / e.total) * 100);
                if (progressBar) progressBar.style.width = pct + '%';
                if (progressText) progressText.textContent = `업로드 중... ${pct}%`;
            }
        });

        xhr.addEventListener('load', () => {
            if (progressText) progressText.textContent = '처리 중...';
            if (xhr.status >= 200 && xhr.status < 300) {
                const contentType = xhr.getResponseHeader('Content-Type') || '';
                if (contentType.includes('application/json')) {
                    try {
                        resolve(JSON.parse(xhr.responseText));
                    } catch {
                        resolve(xhr.responseText);
                    }
                } else {
                    // Binary file response
                    resolve({
                        blob: xhr.response,
                        filename: getFilenameFromHeader(xhr)
                    });
                }
            } else {
                let msg = '처리 중 오류가 발생했습니다.';
                try {
                    const data = JSON.parse(xhr.responseText);
                    if (data.error) msg = data.error;
                } catch {}
                reject(new Error(msg));
            }
        });

        xhr.addEventListener('error', () => {
            reject(new Error('네트워크 오류가 발생했습니다.'));
        });

        xhr.open('POST', url);

        // If expecting binary response
        if (opts.responseType) {
            xhr.responseType = opts.responseType;
        }

        xhr.send(formData);
    });
}

function getFilenameFromHeader(xhr) {
    const disposition = xhr.getResponseHeader('Content-Disposition');
    if (!disposition) return 'output.pdf';
    const match = disposition.match(/filename\*?=(?:UTF-8''|"?)([^";]+)/i);
    if (match) return decodeURIComponent(match[1].replace(/"/g, ''));
    return 'output.pdf';
}

/* ===== Download Blob ===== */
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/* ===== Error Display ===== */
function showError(msg) {
    const el = document.querySelector('.error-msg');
    if (el) {
        el.textContent = msg;
        el.classList.add('active');
    }
}

function hideError() {
    const el = document.querySelector('.error-msg');
    if (el) el.classList.remove('active');
}

/* ===== Result Display ===== */
function showResult() {
    const el = document.querySelector('.result-area');
    if (el) el.classList.add('active');
}

function hideResult() {
    const el = document.querySelector('.result-area');
    if (el) el.classList.remove('active');
}

function resetProgress() {
    const progressWrap = document.querySelector('.progress-wrap');
    const progressBar = document.querySelector('.progress-bar-inner');
    const progressText = document.querySelector('.progress-text');
    if (progressWrap) progressWrap.classList.remove('active');
    if (progressBar) progressBar.style.width = '0%';
    if (progressText) progressText.textContent = '';
}

/* ===== Validate File Size ===== */
function validateFileSize(file) {
    if (file.size > MAX_FILE_SIZE) {
        showError(`파일 크기가 너무 큽니다 (최대 100MB). 현재: ${formatFileSize(file.size)}`);
        return false;
    }
    return true;
}
