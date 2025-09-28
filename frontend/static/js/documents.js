// Documents page specific JavaScript

let currentPage = 1;
let totalPages = 1;
let currentFilters = {};
let selectedDocuments = new Set();

document.addEventListener('DOMContentLoaded', function() {
    initializeDocumentsPage();
});

function initializeDocumentsPage() {
    initializeFilters();
    initializeBulkActions();
    initializePagination();
    initializeSearch();
    loadDocuments();
}

function initializeFilters() {
    // Initialize filter change handlers for individual filters
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', handleFilterChange);
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', handleFilterChange);
    }
    
    // Initialize clear filters button
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }
    
    // Initialize refresh button
    const refreshBtn = document.getElementById('refreshDocumentsBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadDocuments);
    }
}

function initializeDateRangePicker() {
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    if (startDate && endDate) {
        // Set max date to today
        const today = new Date().toISOString().split('T')[0];
        startDate.setAttribute('max', today);
        endDate.setAttribute('max', today);
        
        // Ensure end date is not before start date
        startDate.addEventListener('change', function() {
            endDate.setAttribute('min', this.value);
        });
        
        endDate.addEventListener('change', function() {
            startDate.setAttribute('max', this.value);
        });
    }
}

function handleFilterChange() {
    currentPage = 1;
    updateFiltersFromForm();
    loadDocuments();
}

function updateFiltersFromForm() {
    // Get filter values directly from the filter elements
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const searchInput = document.getElementById('searchInput');
    
    currentFilters = {};
    
    // Add filters if they have values
    if (statusFilter && statusFilter.value.trim() !== '') {
        currentFilters['status'] = statusFilter.value;
    }
    
    if (categoryFilter && categoryFilter.value.trim() !== '') {
        currentFilters['category'] = categoryFilter.value;
    }
    
    if (searchInput && searchInput.value.trim() !== '') {
        currentFilters['search'] = searchInput.value;
    }
}

function clearFilters() {
    // Reset filter values directly
    const statusFilter = document.getElementById('statusFilter');
    const categoryFilter = document.getElementById('categoryFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) statusFilter.value = '';
    if (categoryFilter) categoryFilter.value = '';
    if (searchInput) searchInput.value = '';
    
    // Clear filters object and reset to first page
    currentFilters = {};
    currentPage = 1;
    
    // Reload documents with cleared filters
    console.log('Filters cleared, reloading documents');
    loadDocuments();
    
    // Add visual feedback
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-info alert-dismissible fade show mt-3';
    alertDiv.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        Filters have been reset.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const filterCard = document.querySelector('.card:has(#statusFilter)');
    if (filterCard) {
        filterCard.parentNode.insertBefore(alertDiv, filterCard.nextSibling);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 300);
        }, 3000);
    }
}

function initializeBulkActions() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const bulkActionsContainer = document.getElementById('bulkActions');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', handleSelectAll);
    }
    
    // Initialize bulk action buttons
    const bulkProcessBtn = document.getElementById('bulkProcess');
    const bulkDeleteBtn = document.getElementById('bulkDelete');
    const bulkExportBtn = document.getElementById('bulkExport');
    
    if (bulkProcessBtn) {
        bulkProcessBtn.addEventListener('click', bulkProcessDocuments);
    }
    
    if (bulkDeleteBtn) {
        bulkDeleteBtn.addEventListener('click', bulkDeleteDocuments);
    }
    
    if (bulkExportBtn) {
        bulkExportBtn.addEventListener('click', bulkExportDocuments);
    }
}

function handleSelectAll(e) {
    const isChecked = e.target.checked;
    const documentCheckboxes = document.querySelectorAll('.document-checkbox');
    
    documentCheckboxes.forEach(checkbox => {
        checkbox.checked = isChecked;
        if (isChecked) {
            selectedDocuments.add(checkbox.value);
        } else {
            selectedDocuments.delete(checkbox.value);
        }
    });
    
    updateBulkActions();
}

function handleDocumentSelect(checkbox) {
    if (checkbox.checked) {
        selectedDocuments.add(checkbox.value);
    } else {
        selectedDocuments.delete(checkbox.value);
    }
    
    updateSelectAllState();
    updateBulkActions();
}

function updateSelectAllState() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const documentCheckboxes = document.querySelectorAll('.document-checkbox');
    
    if (!selectAllCheckbox || documentCheckboxes.length === 0) return;
    
    const checkedCount = Array.from(documentCheckboxes).filter(cb => cb.checked).length;
    
    if (checkedCount === 0) {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = false;
    } else if (checkedCount === documentCheckboxes.length) {
        selectAllCheckbox.checked = true;
        selectAllCheckbox.indeterminate = false;
    } else {
        selectAllCheckbox.checked = false;
        selectAllCheckbox.indeterminate = true;
    }
}

function updateBulkActions() {
    const bulkActionsContainer = document.getElementById('bulkActions');
    const selectedCount = selectedDocuments.size;
    
    if (bulkActionsContainer) {
        if (selectedCount > 0) {
            bulkActionsContainer.style.display = 'block';
            bulkActionsContainer.querySelector('.selected-count').textContent = selectedCount;
        } else {
            bulkActionsContainer.style.display = 'none';
        }
    }
}

function initializePagination() {
    // Pagination is handled in loadDocuments and renderPagination
}

function initializeSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    // Debounced search to avoid too many requests while typing
    const debouncedSearch = debounce(() => {
        currentPage = 1;
        updateFiltersFromForm();
        loadDocuments();
    }, 300);
    
    // Handle input events for real-time search
    searchInput.addEventListener('input', debouncedSearch);
    
    // Also handle the Enter key for immediate search
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            currentPage = 1;
            updateFiltersFromForm();
            loadDocuments();
        }
    });
}

function loadDocuments() {
    const container = document.getElementById('documentsContainer');
    if (!container) return;

    // Show appropriate loading message based on filters
    const isSearching = currentFilters.search || currentFilters.status || currentFilters.category;
    const loadingMessage = isSearching ? 'Searching documents...' : 'Loading documents...';
    
    IDP.showLoading(container, loadingMessage);
    
    // Build query parameters
    const params = new URLSearchParams({
        page: currentPage,
        ...currentFilters
    });
    
    console.log('Loading documents with filters:', currentFilters);
    
    IDP.apiRequest(`/api/documents?${params.toString()}`)
        .then(data => {
            if (data.success) {
                renderDocuments(data.documents, isSearching);
                updatePagination(data.pagination);
            } else {
                throw new Error(data.error || 'Failed to load documents');
            }
        })
        .catch(error => {
            console.error('Error loading documents:', error);
            IDP.showError(container, error.message, 'loadDocuments()');
        });
}

function renderDocuments(documents, isSearching = false) {
    const container = document.getElementById('documentsContainer');
    if (!container) return;

    if (documents.length === 0) {
        // Different message for search vs. empty state
        if (isSearching) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-4x text-muted mb-3 opacity-50"></i>
                    <h5>No matching documents found</h5>
                    <p class="text-muted">Try different search terms or filters.</p>
                    <button class="btn btn-outline-secondary" onclick="clearFilters()">
                        <i class="fas fa-times me-2"></i>
                        Clear Filters
                    </button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-folder-open fa-4x text-muted mb-3 opacity-50"></i>
                    <h5>No documents found</h5>
                    <p class="text-muted">Upload your first document to get started.</p>
                    <a href="/upload" class="btn btn-primary">
                        <i class="fas fa-upload me-2"></i>
                        Upload Documents
                    </a>
                </div>
            `;
        }
        return;
    }

    const html = documents.map(doc => `
        <div class="col-md-6 col-lg-4">
            <div class="card document-card h-100" data-doc-id="${doc.id}">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <div class="form-check">
                        <input class="form-check-input document-checkbox" 
                               type="checkbox" 
                               value="${doc.id}"
                               onchange="handleDocumentSelect(this)">
                    </div>
                    <span class="badge ${getStatusBadgeClass(doc.status)}">${doc.status}</span>
                </div>
                <div class="card-body">
                    <div class="d-flex align-items-start mb-3">
                        <div class="flex-shrink-0">
                            <i class="fas ${getDocumentIcon(doc.file_type)} fa-2x text-primary"></i>
                        </div>
                        <div class="flex-grow-1 ms-3">
                            <h6 class="card-title mb-1" title="${doc.filename}">
                                ${truncateText(doc.filename, 30)}
                            </h6>
                            <small class="text-muted">
                                ${IDP.formatFileSize(doc.file_size)} • ${doc.file_type}
                            </small>
                        </div>
                    </div>
                    
                    <div class="document-info">
                        <div class="row g-2 mb-2">
                            <div class="col-6">
                                <small class="text-muted d-block">Upload Date</small>
                                <small>${IDP.formatDate(doc.upload_date)}</small>
                            </div>
                            <div class="col-6">
                                <small class="text-muted d-block">Department</small>
                                <small>${doc.department || 'Unassigned'}</small>
                            </div>
                        </div>
                        
                        ${doc.document_type ? `
                            <div class="mb-2">
                                <small class="text-muted d-block">Document Type</small>
                                <span class="badge bg-light text-dark">${doc.document_type}</span>
                            </div>
                        ` : ''}
                        
                        ${doc.extracted_text ? `
                            <div class="mb-2">
                                <small class="text-muted d-block">Content Preview</small>
                                <p class="small text-truncate mb-0" title="${doc.extracted_text}">
                                    ${truncateText(doc.extracted_text, 100)}
                                </p>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <div class="card-footer bg-transparent">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="btn-group btn-group-sm" role="group">
                            <a href="/document/${doc.id}" class="btn btn-outline-primary">
                                <i class="fas fa-eye"></i>
                            </a>
                            <button class="btn btn-outline-secondary" onclick="downloadDocument('${doc.id}')">
                                <i class="fas fa-download"></i>
                            </button>
                            ${doc.status === 'failed' ? `
                                <button class="btn btn-outline-warning" onclick="processDocument('${doc.id}')">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            ` : ''}
                        </div>
                        
                        <div class="dropdown">
                            <button class="btn btn-sm btn-outline-secondary" 
                                    type="button" 
                                    data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li>
                                    <a class="dropdown-item" href="/document/${doc.id}">
                                        <i class="fas fa-eye me-2"></i>View Details
                                    </a>
                                </li>
                                <li>
                                    <button class="dropdown-item" onclick="downloadDocument('${doc.id}')">
                                        <i class="fas fa-download me-2"></i>Download
                                    </button>
                                </li>
                                ${doc.status === 'failed' ? `
                                    <li>
                                        <button class="dropdown-item" onclick="processDocument('${doc.id}')">
                                            <i class="fas fa-sync-alt me-2"></i>Reprocess
                                        </button>
                                    </li>
                                ` : ''}
                                <li><hr class="dropdown-divider"></li>
                                <li>
                                    <button class="dropdown-item text-danger" onclick="deleteDocument('${doc.id}')">
                                        <i class="fas fa-trash me-2"></i>Delete
                                    </button>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `).join('');

    container.innerHTML = `<div class="row g-3">${html}</div>`;
    
    // Update selected documents based on current selection
    selectedDocuments.forEach(docId => {
        const checkbox = document.querySelector(`.document-checkbox[value="${docId}"]`);
        if (checkbox) {
            checkbox.checked = true;
        }
    });
    
    updateSelectAllState();
    updateBulkActions();
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

function truncateText(text, maxLength) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function updatePagination(pagination) {
    totalPages = pagination.total_pages;
    currentPage = pagination.current_page;
    
    const paginationContainer = document.getElementById('paginationContainer');
    if (!paginationContainer || totalPages <= 1) {
        paginationContainer.style.display = 'none';
        return;
    }
    
    paginationContainer.style.display = 'block';
    renderPagination(pagination);
}

function renderPagination(pagination) {
    const container = document.getElementById('paginationContainer');
    if (!container) return;

    const { current_page, total_pages, has_prev, has_next } = pagination;
    
    let html = '<nav><ul class="pagination justify-content-center">';
    
    // Previous button
    html += `
        <li class="page-item ${!has_prev ? 'disabled' : ''}">
            <button class="page-link" onclick="goToPage(${current_page - 1})" ${!has_prev ? 'disabled' : ''}>
                <i class="fas fa-chevron-left"></i>
            </button>
        </li>
    `;
    
    // Page numbers
    const startPage = Math.max(1, current_page - 2);
    const endPage = Math.min(total_pages, current_page + 2);
    
    if (startPage > 1) {
        html += `
            <li class="page-item">
                <button class="page-link" onclick="goToPage(1)">1</button>
            </li>
        `;
        if (startPage > 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        html += `
            <li class="page-item ${i === current_page ? 'active' : ''}">
                <button class="page-link" onclick="goToPage(${i})">${i}</button>
            </li>
        `;
    }
    
    if (endPage < total_pages) {
        if (endPage < total_pages - 1) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        html += `
            <li class="page-item">
                <button class="page-link" onclick="goToPage(${total_pages})">${total_pages}</button>
            </li>
        `;
    }
    
    // Next button
    html += `
        <li class="page-item ${!has_next ? 'disabled' : ''}">
            <button class="page-link" onclick="goToPage(${current_page + 1})" ${!has_next ? 'disabled' : ''}>
                <i class="fas fa-chevron-right"></i>
            </button>
        </li>
    `;
    
    html += '</ul></nav>';
    
    container.innerHTML = html;
}

function goToPage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    
    currentPage = page;
    loadDocuments();
}

// Document actions
function processDocument(docId) {
    IDP.processDocument(docId)
        .then(data => {
            if (data.success) {
                loadDocuments(); // Refresh the list
            }
        });
}

function downloadDocument(docId) {
    window.open(`/api/download/${docId}`, '_blank');
}

function deleteDocument(docId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    IDP.apiRequest(`/api/document/${docId}`, { method: 'DELETE' })
        .then(data => {
            if (data.success) {
                IDP.showAlert('Document deleted successfully.', 'success');
                selectedDocuments.delete(docId);
                loadDocuments(); // Refresh the list
            } else {
                throw new Error(data.error || 'Failed to delete document');
            }
        })
        .catch(error => {
            IDP.showAlert(`Error deleting document: ${error.message}`, 'danger');
        });
}

// Bulk actions
function bulkProcessDocuments() {
    if (selectedDocuments.size === 0) return;
    
    const docIds = Array.from(selectedDocuments);
    const modal = new bootstrap.Modal(document.getElementById('bulkProcessModal'));
    modal.show();
    
    processBulkDocuments(docIds);
}

function processBulkDocuments(docIds) {
    let completed = 0;
    let errors = 0;
    
    const updateProgress = () => {
        const progress = ((completed + errors) / docIds.length) * 100;
        const progressBar = document.querySelector('#bulkProcessModal .progress-bar');
        const statusText = document.querySelector('#bulkProcessModal .status-text');
        
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        if (statusText) {
            statusText.textContent = `Processing ${completed + errors} of ${docIds.length} documents...`;
        }
    };
    
    const processNext = (index) => {
        if (index >= docIds.length) {
            // All done
            const modal = bootstrap.Modal.getInstance(document.getElementById('bulkProcessModal'));
            modal.hide();
            
            IDP.showAlert(
                `Bulk processing completed. ${completed} successful, ${errors} failed.`,
                errors > 0 ? 'warning' : 'success'
            );
            
            selectedDocuments.clear();
            loadDocuments();
            return;
        }
        
        IDP.processDocument(docIds[index], false)
            .then(() => {
                completed++;
            })
            .catch(() => {
                errors++;
            })
            .finally(() => {
                updateProgress();
                processNext(index + 1);
            });
    };
    
    processNext(0);
}

function bulkDeleteDocuments() {
    if (selectedDocuments.size === 0) return;
    
    const count = selectedDocuments.size;
    if (!confirm(`Are you sure you want to delete ${count} document${count > 1 ? 's' : ''}? This action cannot be undone.`)) {
        return;
    }
    
    const docIds = Array.from(selectedDocuments);
    
    Promise.all(docIds.map(docId => 
        IDP.apiRequest(`/api/document/${docId}`, { method: 'DELETE' })
    ))
        .then(results => {
            const successful = results.filter(r => r.success).length;
            const failed = results.length - successful;
            
            if (failed === 0) {
                IDP.showAlert(`${successful} document${successful > 1 ? 's' : ''} deleted successfully.`, 'success');
            } else {
                IDP.showAlert(`${successful} document${successful > 1 ? 's' : ''} deleted, ${failed} failed.`, 'warning');
            }
            
            selectedDocuments.clear();
            loadDocuments();
        })
        .catch(error => {
            IDP.showAlert(`Error during bulk delete: ${error.message}`, 'danger');
        });
}

function bulkExportDocuments() {
    if (selectedDocuments.size === 0) return;
    
    const docIds = Array.from(selectedDocuments);
    const params = new URLSearchParams();
    docIds.forEach(id => params.append('doc_ids', id));
    
    window.open(`/api/export?${params.toString()}`, '_blank');
}

// Utility function
// Utility function for debouncing
function debounce(func, delay) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), delay);
    };
}

// Keyboard shortcuts for documents page
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + A: Select all documents
    if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = !selectAllCheckbox.checked;
            handleSelectAll({ target: selectAllCheckbox });
        }
    }
});
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + A: Select all documents
    if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
        e.preventDefault();
        const selectAllCheckbox = document.getElementById('selectAll');
        if (selectAllCheckbox) {
            selectAllCheckbox.checked = !selectAllCheckbox.checked;
            handleSelectAll({ target: selectAllCheckbox });
        }
    }
    
    // Delete: Delete selected documents
    if (e.key === 'Delete' && selectedDocuments.size > 0) {
        e.preventDefault();
        bulkDeleteDocuments();
    }
    
    // Ctrl/Cmd + P: Process selected documents
    if ((e.ctrlKey || e.metaKey) && e.key === 'p' && selectedDocuments.size > 0) {
        e.preventDefault();
        bulkProcessDocuments();
    }
    
    // Ctrl/Cmd + E: Export selected documents
    if ((e.ctrlKey || e.metaKey) && e.key === 'e' && selectedDocuments.size > 0) {
        e.preventDefault();
        bulkExportDocuments();
    }
});