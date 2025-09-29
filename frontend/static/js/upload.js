// Upload page specific JavaScript

let uploadQueue = [];
let activeUploads = 0;
const maxConcurrentUploads = 3;

document.addEventListener('DOMContentLoaded', function() {
    initializeUploadPage();
});

function initializeUploadPage() {
    initializeDropZone();
    initializeFileInput();
    initializeBulkActions();
    updateUploadButton();
}

function initializeDropZone() {
    const dropZone = document.getElementById('dropZone');
    if (!dropZone) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click to open file dialog
    dropZone.addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    const dropZone = document.getElementById('dropZone');
    dropZone.classList.add('drag-over');
}

function unhighlight(e) {
    const dropZone = document.getElementById('dropZone');
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function initializeFileInput() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput) return;

    fileInput.addEventListener('change', function(e) {
        handleFiles(e.target.files);
    });
}

function handleFiles(files) {
    const fileArray = Array.from(files);
    const validFiles = fileArray.filter(validateFile);
    
    if (validFiles.length !== fileArray.length) {
        const invalidCount = fileArray.length - validFiles.length;
        IDP.showAlert(`${invalidCount} file(s) were skipped due to invalid format or size.`, 'warning');
    }
    
    validFiles.forEach(file => {
        addFileToQueue(file);
    });
    
    updateUploadButton();
}

function validateFile(file) {
    // Validate file type
    const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/tiff',
        'image/gif',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    
    if (!allowedTypes.includes(file.type)) {
        return false;
    }
    
    // Validate file size (100MB max)
    const maxSize = 100 * 1024 * 1024; // 100MB in bytes
    if (file.size > maxSize) {
        return false;
    }
    
    return true;
}

function addFileToQueue(file) {
    const fileId = 'file-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    const fileInfo = {
        id: fileId,
        file: file,
        status: 'pending',
        progress: 0,
        error: null
    };
    
    uploadQueue.push(fileInfo);
    renderFileQueue();
}

function renderFileQueue() {
    const queueContainer = document.getElementById('uploadQueue');
    if (!queueContainer) return;

    if (uploadQueue.length === 0) {
        queueContainer.innerHTML = '<p class="text-muted text-center">No files selected</p>';
        return;
    }

    queueContainer.innerHTML = uploadQueue.map(fileInfo => `
        <div class="upload-item" id="${fileInfo.id}">
            <div class="d-flex align-items-center">
                <div class="flex-shrink-0">
                    <i class="fas ${getFileIcon(fileInfo.file)} fa-2x text-primary"></i>
                </div>
                <div class="flex-grow-1 ms-3">
                    <h6 class="mb-1">${fileInfo.file.name}</h6>
                    <small class="text-muted">
                        ${IDP.formatFileSize(fileInfo.file.size)} • ${fileInfo.file.type}
                    </small>
                    <div class="progress mt-2" style="height: 6px;">
                        <div class="progress-bar ${getProgressBarClass(fileInfo.status)}" 
                             role="progressbar" 
                             style="width: ${fileInfo.progress}%">
                        </div>
                    </div>
                    <div class="mt-1">
                        <small class="status-text ${getStatusClass(fileInfo.status)}">
                            ${getStatusText(fileInfo)}
                        </small>
                    </div>
                </div>
                <div class="flex-shrink-0 ms-3">
                    ${getActionButtons(fileInfo)}
                </div>
            </div>
        </div>
    `).join('');
}

function getFileIcon(file) {
    const type = file.type.toLowerCase();
    
    if (type.includes('pdf')) return 'fa-file-pdf';
    if (type.includes('image')) return 'fa-file-image';
    if (type.includes('word') || type.includes('document')) return 'fa-file-word';
    if (type.includes('excel') || type.includes('spreadsheet')) return 'fa-file-excel';
    if (type.includes('text')) return 'fa-file-alt';
    
    return 'fa-file';
}

function getProgressBarClass(status) {
    switch (status) {
        case 'uploading': return 'bg-primary';
        case 'processing': return 'bg-warning';
        case 'completed': return 'bg-success';
        case 'error': return 'bg-danger';
        default: return 'bg-secondary';
    }
}

function getStatusClass(status) {
    switch (status) {
        case 'completed': return 'text-success';
        case 'error': return 'text-danger';
        case 'processing_error': return 'text-warning';
        case 'uploading': return 'text-primary';
        case 'processing': return 'text-info';
        default: return 'text-muted';
    }
}

function getStatusText(fileInfo) {
    switch (fileInfo.status) {
        case 'pending': return 'Waiting to upload';
        case 'uploading': return `Uploading... ${Math.round(fileInfo.progress)}%`;
        case 'processing': return 'Processing document...';
        case 'completed': 
            if (fileInfo.documentData) {
                return `Processed: ${fileInfo.documentData.document_type} → ${fileInfo.documentData.department}`;
            }
            return 'Upload and processing completed';
        case 'processing_error': return `Uploaded but ${fileInfo.error || 'processing failed'}`;
        case 'error': return fileInfo.error || 'Upload failed';
        default: return 'Unknown status';
    }
}

function getActionButtons(fileInfo) {
    switch (fileInfo.status) {
        case 'pending':
            return `
                <button class="btn btn-sm btn-outline-danger" onclick="removeFromQueue('${fileInfo.id}')">
                    <i class="fas fa-times"></i>
                </button>
            `;
        case 'uploading':
        case 'processing':
            return `
                <button class="btn btn-sm btn-outline-warning" onclick="cancelUpload('${fileInfo.id}')">
                    <i class="fas fa-stop"></i>
                </button>
            `;
        case 'completed':
            return `
                <button class="btn btn-sm btn-outline-primary" onclick="viewDocument('${fileInfo.documentId}')">
                    <i class="fas fa-eye"></i>
                </button>
            `;
        case 'processing_error':
            return `
                <button class="btn btn-sm btn-outline-primary" onclick="viewDocument('${fileInfo.documentId}')">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-warning ms-1" onclick="reprocessDocument('${fileInfo.documentId}')">
                    <i class="fas fa-sync-alt"></i>
                </button>
            `;
        case 'error':
            return `
                <button class="btn btn-sm btn-outline-primary" onclick="retryUpload('${fileInfo.id}')">
                    <i class="fas fa-sync-alt"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger ms-1" onclick="removeFromQueue('${fileInfo.id}')">
                    <i class="fas fa-times"></i>
                </button>
            `;
        default:
            return '';
    }
}

function removeFromQueue(fileId) {
    uploadQueue = uploadQueue.filter(file => file.id !== fileId);
    renderFileQueue();
    updateUploadButton();
}

function cancelUpload(fileId) {
    const fileInfo = uploadQueue.find(file => file.id === fileId);
    if (fileInfo && fileInfo.xhr) {
        fileInfo.xhr.abort();
        fileInfo.status = 'error';
        fileInfo.error = 'Upload cancelled';
        activeUploads--;
        renderFileQueue();
        processNextInQueue();
    }
}

function retryUpload(fileId) {
    const fileInfo = uploadQueue.find(file => file.id === fileId);
    if (fileInfo) {
        fileInfo.status = 'pending';
        fileInfo.progress = 0;
        fileInfo.error = null;
        renderFileQueue();
        processUploadQueue();
    }
}

function viewDocument(documentId) {
    window.location.href = `/document/${documentId}`;
}

function updateUploadButton() {
    const uploadButton = document.getElementById('uploadButton');
    const clearButton = document.getElementById('clearQueueButton');
    
    if (!uploadButton || !clearButton) return;

    const pendingFiles = uploadQueue.filter(file => file.status === 'pending');
    const hasFiles = uploadQueue.length > 0;
    
    uploadButton.disabled = pendingFiles.length === 0;
    clearButton.style.display = hasFiles ? 'inline-block' : 'none';
    
    if (pendingFiles.length > 0) {
        uploadButton.innerHTML = `
            <i class="fas fa-upload me-2"></i>
            Upload ${pendingFiles.length} file${pendingFiles.length > 1 ? 's' : ''}
        `;
    } else {
        uploadButton.innerHTML = `
            <i class="fas fa-upload me-2"></i>
            Upload Files
        `;
    }
}

function initializeBulkActions() {
    const uploadButton = document.getElementById('uploadButton');
    const clearButton = document.getElementById('clearQueueButton');
    
    if (uploadButton) {
        uploadButton.addEventListener('click', startUpload);
    }
    
    if (clearButton) {
        clearButton.addEventListener('click', clearQueue);
    }
}

function startUpload() {
    const pendingFiles = uploadQueue.filter(file => file.status === 'pending');
    if (pendingFiles.length === 0) return;
    
    processUploadQueue();
}

function clearQueue() {
    // Only remove pending and error files
    uploadQueue = uploadQueue.filter(file => 
        file.status === 'uploading' || 
        file.status === 'processing' || 
        file.status === 'completed'
    );
    renderFileQueue();
    updateUploadButton();
}

function processUploadQueue() {
    while (activeUploads < maxConcurrentUploads) {
        const nextFile = uploadQueue.find(file => file.status === 'pending');
        if (!nextFile) break;
        
        uploadFile(nextFile);
        activeUploads++;
    }
}

function processNextInQueue() {
    const nextFile = uploadQueue.find(file => file.status === 'pending');
    if (nextFile && activeUploads < maxConcurrentUploads) {
        uploadFile(nextFile);
        activeUploads++;
    }
    
    updateUploadButton();
}

function uploadFile(fileInfo) {
    fileInfo.status = 'uploading';
    fileInfo.progress = 0;
    renderFileQueue();
    
    const formData = new FormData();
    formData.append('file', fileInfo.file);
    
    const xhr = new XMLHttpRequest();
    fileInfo.xhr = xhr;
    
    // Upload progress
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            fileInfo.progress = (e.loaded / e.total) * 100;
            renderFileQueue();
        }
    });
    
    // Upload complete
    xhr.addEventListener('load', () => {
        activeUploads--;
        
        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    fileInfo.progress = 100;
                    fileInfo.documentId = response.document_id;
                    
                    // Document is now automatically processed during upload
                    if (response.document && response.document.status === 'processed') {
                        fileInfo.status = 'completed';
                        fileInfo.documentData = response.document; // Store the processed document data
                        
                        // Show processing results with AI classification details
                        let message = `${fileInfo.file.name} uploaded and processed successfully!\n`;
                        message += `Classification: ${response.document.document_type}\n`;
                        message += `Department: ${response.document.department}\n`;
                        
                        // Add AI classification details if available
                        if (response.classification) {
                            const confidence = Math.round(response.classification.confidence * 100);
                            message += `Confidence: ${confidence}%\n`;
                            message += `Method: ${response.classification.method === 'gemini_api' ? 'AI-Powered' : 'Fallback'}`;
                        }
                        
                        IDP.showAlert(message, 'success');
                        
                    } else if (response.document && response.document.status === 'failed') {
                        fileInfo.status = 'processing_error';
                        fileInfo.error = response.processing_error || 'Processing failed after upload';
                        IDP.showAlert(`${fileInfo.file.name} uploaded but processing failed`, 'warning');
                        
                    } else {
                        // Fallback for any other status
                        fileInfo.status = 'completed';
                        IDP.showAlert(`${fileInfo.file.name} uploaded successfully`, 'info');
                    }
                } else {
                    fileInfo.status = 'error';
                    fileInfo.error = response.error || 'Upload failed';
                }
            } catch (e) {
                fileInfo.status = 'error';
                fileInfo.error = 'Invalid response from server';
            }
        } else {
            fileInfo.status = 'error';
            fileInfo.error = `Upload failed with status: ${xhr.status}`;
        }
        
        renderFileQueue();
        processNextInQueue();
    });
    
    // Upload error
    xhr.addEventListener('error', () => {
        activeUploads--;
        fileInfo.status = 'error';
        fileInfo.error = 'Network error';
        renderFileQueue();
        processNextInQueue();
    });
    
    // Upload aborted
    xhr.addEventListener('abort', () => {
        activeUploads--;
        // Status already set by cancelUpload
        processNextInQueue();
    });
    
    xhr.open('POST', '/api/upload');
    xhr.send(formData);
}

function processDocumentAfterUpload(fileInfo, documentId) {
    fileInfo.status = 'processing';
    renderFileQueue();
    
    // Process document
    IDP.processDocument(documentId, false)
        .then(data => {
            if (data.success) {
                IDP.showAlert(`${fileInfo.file.name} processed successfully!`, 'success');
            }
        })
        .catch(error => {
            IDP.showAlert(`Error processing ${fileInfo.file.name}: ${error.message}`, 'warning');
        })
        .finally(() => {
            renderFileQueue();
        });
}

// Keyboard shortcuts for upload page
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + O: Open file dialog
    if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
        e.preventDefault();
        document.getElementById('fileInput').click();
    }
    
    // Ctrl/Cmd + Enter: Start upload
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        const uploadButton = document.getElementById('uploadButton');
        if (uploadButton && !uploadButton.disabled) {
            startUpload();
        }
    }
    
    // Delete: Clear queue
    if (e.key === 'Delete' && e.shiftKey) {
        e.preventDefault();
        clearQueue();
    }
});

// Function to reprocess a document that failed during processing
function reprocessDocument(documentId) {
    if (!documentId) return;
    
    IDP.processDocument(documentId)
        .then(data => {
            if (data.success) {
                IDP.showAlert('Document reprocessed successfully!', 'success');
                // Update the file info in the queue if it exists
                const fileInfo = uploadQueue.find(f => f.documentId == documentId);
                if (fileInfo) {
                    fileInfo.status = 'completed';
                    fileInfo.documentData = data.document;
                    renderFileQueue();
                }
            } else {
                IDP.showAlert('Failed to reprocess document', 'danger');
            }
        })
        .catch(error => {
            IDP.showAlert(`Error reprocessing document: ${error.message}`, 'danger');
        });
}