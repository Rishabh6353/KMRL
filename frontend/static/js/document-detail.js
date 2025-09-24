// Document detail page specific JavaScript

let currentDocument = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeDocumentDetailPage();
});

function initializeDocumentDetailPage() {
    // Get document ID from URL
    const pathParts = window.location.pathname.split('/');
    const docId = pathParts[pathParts.length - 1];
    
    if (docId && docId !== 'document') {
        loadDocumentDetails(docId);
    }
    
    initializeTabNavigation();
    initializeActionButtons();
    initializeTextSelection();
}

function loadDocumentDetails(docId) {
    const container = document.getElementById('documentContent');
    if (!container) return;

    IDP.showLoading(container, 'Loading document details...');
    
    IDP.apiRequest(`/api/document/${docId}`)
        .then(data => {
            if (data.success) {
                currentDocument = data.document;
                renderDocumentDetails(data.document);
            } else {
                throw new Error(data.error || 'Failed to load document details');
            }
        })
        .catch(error => {
            IDP.showError(container, error.message, `loadDocumentDetails('${docId}')`);
        });
}

function renderDocumentDetails(document) {
    const container = document.getElementById('documentContent');
    if (!container) return;

    const html = `
        <div class="row">
            <div class="col-lg-8">
                <!-- Document Preview -->
                <div class="card mb-4">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">
                            <i class="fas ${getDocumentIcon(document.file_type)} me-2"></i>
                            ${document.filename}
                        </h5>
                        <span class="badge ${getStatusBadgeClass(document.status)} fs-6">
                            ${document.status}
                        </span>
                    </div>
                    <div class="card-body">
                        ${renderDocumentPreview(document)}
                    </div>
                </div>

                <!-- Tabs for different content -->
                <div class="card">
                    <div class="card-header">
                        <ul class="nav nav-tabs card-header-tabs" id="contentTabs" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="extracted-tab" data-bs-toggle="tab" 
                                        data-bs-target="#extracted" type="button" role="tab">
                                    <i class="fas fa-file-alt me-2"></i>Extracted Text
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="entities-tab" data-bs-toggle="tab" 
                                        data-bs-target="#entities" type="button" role="tab">
                                    <i class="fas fa-tags me-2"></i>Entities
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="summary-tab" data-bs-toggle="tab" 
                                        data-bs-target="#summary" type="button" role="tab">
                                    <i class="fas fa-compress-alt me-2"></i>Summary
                                </button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="keyvalues-tab" data-bs-toggle="tab" 
                                        data-bs-target="#keyvalues" type="button" role="tab">
                                    <i class="fas fa-key me-2"></i>Key-Value Pairs
                                </button>
                            </li>
                        </ul>
                    </div>
                    <div class="card-body">
                        <div class="tab-content" id="contentTabsContent">
                            <div class="tab-pane fade show active" id="extracted" role="tabpanel">
                                ${renderExtractedText(document.extracted_text)}
                            </div>
                            <div class="tab-pane fade" id="entities" role="tabpanel">
                                ${renderEntities(document.extracted_entities)}
                            </div>
                            <div class="tab-pane fade" id="summary" role="tabpanel">
                                ${renderSummary(document.summary)}
                            </div>
                            <div class="tab-pane fade" id="keyvalues" role="tabpanel">
                                ${renderKeyValuePairs(document.key_value_pairs)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-4">
                <!-- Document Information -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h6 class="mb-0">Document Information</h6>
                    </div>
                    <div class="card-body">
                        ${renderDocumentInfo(document)}
                    </div>
                </div>

                <!-- Actions -->
                <div class="card mb-4">
                    <div class="card-header">
                        <h6 class="mb-0">Actions</h6>
                    </div>
                    <div class="card-body">
                        ${renderActionButtons(document)}
                    </div>
                </div>

                <!-- Processing Logs -->
                <div class="card">
                    <div class="card-header">
                        <h6 class="mb-0">Processing Logs</h6>
                    </div>
                    <div class="card-body">
                        ${renderProcessingLogs(document.processing_logs)}
                    </div>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function renderDocumentPreview(document) {
    if (document.file_type && document.file_type.includes('image')) {
        return `
            <div class="text-center">
                <img src="/api/preview/${document.id}" 
                     class="img-fluid rounded" 
                     alt="Document preview"
                     style="max-height: 500px;">
            </div>
        `;
    } else if (document.file_type && document.file_type.includes('pdf')) {
        return `
            <div class="text-center">
                <embed src="/api/preview/${document.id}" 
                       type="application/pdf" 
                       width="100%" 
                       height="500px"
                       class="rounded">
                <p class="mt-2">
                    <a href="/api/download/${document.id}" target="_blank" class="btn btn-outline-primary">
                        <i class="fas fa-external-link-alt me-2"></i>Open in new tab
                    </a>
                </p>
            </div>
        `;
    } else {
        return `
            <div class="text-center py-5">
                <i class="fas ${getDocumentIcon(document.file_type)} fa-4x text-muted mb-3"></i>
                <p class="text-muted">Preview not available for this file type.</p>
                <a href="/api/download/${document.id}" class="btn btn-outline-primary">
                    <i class="fas fa-download me-2"></i>Download File
                </a>
            </div>
        `;
    }
}

function renderDocumentInfo(document) {
    return `
        <div class="row g-3">
            <div class="col-12">
                <strong>File Name:</strong><br>
                <span class="text-break">${document.filename}</span>
            </div>
            <div class="col-6">
                <strong>File Size:</strong><br>
                ${IDP.formatFileSize(document.file_size)}
            </div>
            <div class="col-6">
                <strong>File Type:</strong><br>
                ${document.file_type || 'Unknown'}
            </div>
            <div class="col-6">
                <strong>Upload Date:</strong><br>
                ${IDP.formatDate(document.upload_date)}
            </div>
            <div class="col-6">
                <strong>Status:</strong><br>
                <span class="badge ${getStatusBadgeClass(document.status)}">${document.status}</span>
            </div>
            ${document.document_type ? `
                <div class="col-12">
                    <strong>Document Type:</strong><br>
                    <span class="badge bg-primary">${document.document_type}</span>
                </div>
            ` : ''}
            ${document.department ? `
                <div class="col-12">
                    <strong>Department:</strong><br>
                    <span class="badge bg-secondary">${document.department}</span>
                </div>
            ` : ''}
            ${document.confidence_score ? `
                <div class="col-12">
                    <strong>Confidence Score:</strong><br>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar" 
                             role="progressbar" 
                             style="width: ${document.confidence_score * 100}%">
                            ${Math.round(document.confidence_score * 100)}%
                        </div>
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

function renderActionButtons(document) {
    const buttons = [];
    
    // Download button
    buttons.push(`
        <button class="btn btn-outline-primary w-100 mb-2" onclick="downloadDocument('${document.id}')">
            <i class="fas fa-download me-2"></i>Download
        </button>
    `);
    
    // Process button (if not processed)
    if (document.status === 'uploaded') {
        buttons.push(`
            <button class="btn btn-success w-100 mb-2" onclick="processDocument('${document.id}')">
                <i class="fas fa-cog me-2"></i>Process Document
            </button>
        `);
    }
    
    // Reprocess button (if already processed)
    if (document.status === 'processed' || document.status === 'error') {
        buttons.push(`
            <button class="btn btn-warning w-100 mb-2" onclick="reprocessDocument('${document.id}')">
                <i class="fas fa-sync-alt me-2"></i>Reprocess
            </button>
        `);
    }
    
    // Export button
    buttons.push(`
        <div class="dropdown w-100 mb-2">
            <button class="btn btn-outline-secondary w-100 dropdown-toggle" 
                    type="button" 
                    data-bs-toggle="dropdown">
                <i class="fas fa-share-alt me-2"></i>Export
            </button>
            <ul class="dropdown-menu w-100">
                <li>
                    <button class="dropdown-item" onclick="exportDocument('${document.id}', 'json')">
                        <i class="fas fa-file-code me-2"></i>Export as JSON
                    </button>
                </li>
                <li>
                    <button class="dropdown-item" onclick="exportDocument('${document.id}', 'csv')">
                        <i class="fas fa-file-csv me-2"></i>Export as CSV
                    </button>
                </li>
                <li>
                    <button class="dropdown-item" onclick="exportDocument('${document.id}', 'txt')">
                        <i class="fas fa-file-alt me-2"></i>Export as Text
                    </button>
                </li>
            </ul>
        </div>
    `);
    
    // Delete button
    buttons.push(`
        <button class="btn btn-outline-danger w-100" onclick="deleteDocument('${document.id}')">
            <i class="fas fa-trash me-2"></i>Delete
        </button>
    `);
    
    return buttons.join('');
}

function renderExtractedText(text) {
    if (!text) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-file-alt fa-3x text-muted mb-3"></i>
                <p class="text-muted">No extracted text available.</p>
            </div>
        `;
    }
    
    return `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="mb-0">Extracted Text Content</h6>
            <div>
                <button class="btn btn-sm btn-outline-secondary me-2" onclick="copyText('extractedText')">
                    <i class="fas fa-copy"></i> Copy
                </button>
                <button class="btn btn-sm btn-outline-secondary" onclick="searchInText()">
                    <i class="fas fa-search"></i> Search
                </button>
            </div>
        </div>
        <div class="position-relative">
            <textarea id="extractedText" 
                      class="form-control font-monospace" 
                      rows="15" 
                      readonly>${text}</textarea>
            <div id="searchHighlight" class="position-absolute top-0 start-0 w-100 h-100 pe-none"></div>
        </div>
        <div class="mt-2">
            <small class="text-muted">
                ${text.split(' ').length} words, ${text.length} characters
            </small>
        </div>
    `;
}

function renderEntities(entities) {
    if (!entities || entities.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-tags fa-3x text-muted mb-3"></i>
                <p class="text-muted">No entities extracted.</p>
            </div>
        `;
    }
    
    // Group entities by type
    const groupedEntities = entities.reduce((acc, entity) => {
        if (!acc[entity.type]) {
            acc[entity.type] = [];
        }
        acc[entity.type].push(entity);
        return acc;
    }, {});
    
    const entityTypes = Object.keys(groupedEntities);
    
    return `
        <div class="mb-3">
            <h6>Extracted Entities (${entities.length} total)</h6>
        </div>
        ${entityTypes.map(type => `
            <div class="mb-4">
                <h6 class="text-primary">
                    ${type.toUpperCase()} 
                    <span class="badge bg-primary ms-2">${groupedEntities[type].length}</span>
                </h6>
                <div class="row g-2">
                    ${groupedEntities[type].map(entity => `
                        <div class="col-md-6">
                            <div class="border rounded p-2">
                                <strong>${entity.text}</strong>
                                ${entity.confidence ? `
                                    <br><small class="text-muted">
                                        Confidence: ${Math.round(entity.confidence * 100)}%
                                    </small>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    `;
}

function renderSummary(summary) {
    if (!summary) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-compress-alt fa-3x text-muted mb-3"></i>
                <p class="text-muted">No summary available.</p>
            </div>
        `;
    }
    
    return `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h6 class="mb-0">Document Summary</h6>
            <button class="btn btn-sm btn-outline-secondary" onclick="copyText('summaryText')">
                <i class="fas fa-copy"></i> Copy
            </button>
        </div>
        <div class="bg-light rounded p-3">
            <p id="summaryText" class="mb-0">${summary}</p>
        </div>
        <div class="mt-2">
            <small class="text-muted">
                ${summary.split(' ').length} words, ${summary.length} characters
            </small>
        </div>
    `;
}

function renderKeyValuePairs(keyValuePairs) {
    if (!keyValuePairs || keyValuePairs.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-key fa-3x text-muted mb-3"></i>
                <p class="text-muted">No key-value pairs extracted.</p>
            </div>
        `;
    }
    
    return `
        <div class="mb-3">
            <h6>Extracted Key-Value Pairs (${keyValuePairs.length} total)</h6>
        </div>
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th>Key</th>
                        <th>Value</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    ${keyValuePairs.map(pair => `
                        <tr>
                            <td><strong>${pair.key}</strong></td>
                            <td>${pair.value}</td>
                            <td>
                                ${pair.confidence ? `
                                    <span class="badge bg-${getConfidenceBadgeClass(pair.confidence)}">
                                        ${Math.round(pair.confidence * 100)}%
                                    </span>
                                ` : 'N/A'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function renderProcessingLogs(logs) {
    if (!logs || logs.length === 0) {
        return `
            <div class="text-center py-4">
                <i class="fas fa-list fa-3x text-muted mb-3"></i>
                <p class="text-muted">No processing logs available.</p>
            </div>
        `;
    }
    
    return `
        <div class="timeline">
            ${logs.map(log => `
                <div class="timeline-item">
                    <div class="timeline-marker ${getLogMarkerClass(log.status)}">
                        <i class="fas ${getLogIcon(log.status)}"></i>
                    </div>
                    <div class="timeline-content">
                        <h6 class="mb-1">${log.step}</h6>
                        <p class="mb-1 text-muted">${log.message}</p>
                        <small class="text-muted">${IDP.formatDate(log.timestamp)}</small>
                        ${log.duration ? `
                            <br><small class="text-muted">Duration: ${log.duration}ms</small>
                        ` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function getConfidenceBadgeClass(confidence) {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'danger';
}

function getLogMarkerClass(status) {
    switch (status) {
        case 'success': return 'bg-success';
        case 'error': return 'bg-danger';
        case 'warning': return 'bg-warning';
        default: return 'bg-secondary';
    }
}

function getLogIcon(status) {
    switch (status) {
        case 'success': return 'fa-check';
        case 'error': return 'fa-times';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info';
    }
}

function getDocumentIcon(fileType) {
    if (!fileType) return 'fa-file';
    
    const type = fileType.toLowerCase();
    
    if (type.includes('pdf')) return 'fa-file-pdf';
    if (type.includes('image')) return 'fa-file-image';
    if (type.includes('word') || type.includes('document')) return 'fa-file-word';
    if (type.includes('excel') || type.includes('spreadsheet')) return 'fa-file-excel';
    if (type.includes('text')) return 'fa-file-alt';
    
    return 'fa-file';
}

function getStatusBadgeClass(status) {
    const classes = {
        'uploaded': 'bg-secondary',
        'processing': 'bg-warning',
        'processed': 'bg-success',
        'error': 'bg-danger'
    };
    return classes[status] || 'bg-secondary';
}

function initializeTabNavigation() {
    // Bootstrap tabs are automatically initialized
}

function initializeActionButtons() {
    // Action buttons are rendered with onclick handlers
}

function initializeTextSelection() {
    // Allow text selection and copying in text areas
}

// Action functions
function downloadDocument(docId) {
    window.open(`/api/download/${docId}`, '_blank');
}

function processDocument(docId) {
    IDP.processDocument(docId)
        .then(data => {
            if (data.success) {
                // Reload page to show updated status
                window.location.reload();
            }
        });
}

function reprocessDocument(docId) {
    if (!confirm('Are you sure you want to reprocess this document? This will overwrite existing extracted data.')) {
        return;
    }
    
    processDocument(docId);
}

function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    IDP.apiRequest(`/api/document/${docId}`, { method: 'DELETE' })
        .then(data => {
            if (data.success) {
                IDP.showAlert('Document deleted successfully.', 'success');
                // Redirect to documents page
                window.location.href = '/documents';
            } else {
                throw new Error(data.error || 'Failed to delete document');
            }
        })
        .catch(error => {
            IDP.showAlert(`Error deleting document: ${error.message}`, 'danger');
        });
}

function exportDocument(docId, format) {
    window.open(`/api/export/${docId}?format=${format}`, '_blank');
}

function copyText(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        IDP.copyToClipboard(element.value || element.textContent);
    }
}

function searchInText() {
    const searchTerm = prompt('Enter text to search for:');
    if (!searchTerm) return;
    
    const textArea = document.getElementById('extractedText');
    if (!textArea) return;
    
    const text = textArea.value;
    const searchIndex = text.toLowerCase().indexOf(searchTerm.toLowerCase());
    
    if (searchIndex !== -1) {
        textArea.focus();
        textArea.setSelectionRange(searchIndex, searchIndex + searchTerm.length);
        textArea.scrollTop = Math.max(0, (searchIndex / text.length) * textArea.scrollHeight - textArea.clientHeight / 2);
        
        IDP.showAlert(`Found "${searchTerm}" at position ${searchIndex}`, 'success');
    } else {
        IDP.showAlert(`"${searchTerm}" not found in the text`, 'warning');
    }
}