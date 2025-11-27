/**
 * Image Editor with OCR - Frontend Application Logic
 * Handles image upload, OCR extraction, form generation, and regeneration
 */

// Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// Global state
let sessionId = null;
let extractedData = null;
let currentFields = [];

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const editSection = document.getElementById('editSection');
const previewSection = document.getElementById('previewSection');
const editForm = document.getElementById('editForm');
const uploadProgress = document.getElementById('uploadProgress');
const loadingOverlay = document.getElementById('loadingOverlay');
const toastContainer = document.getElementById('toastContainer');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadZone.addEventListener('dragover', handleDragOver);
    uploadZone.addEventListener('dragleave', handleDragLeave);
    uploadZone.addEventListener('drop', handleDrop);
    
    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());
}

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

/**
 * Handle drag over
 */
function handleDragOver(event) {
    event.preventDefault();
    uploadZone.classList.add('drag-over');
}

/**
 * Handle drag leave
 */
function handleDragLeave(event) {
    event.preventDefault();
    uploadZone.classList.remove('drag-over');
}

/**
 * Handle file drop
 */
function handleDrop(event) {
    event.preventDefault();
    uploadZone.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
        uploadFile(file);
    } else {
        showToast('Please upload an image file', 'error');
    }
}

/**
 * Upload file to server for OCR extraction
 */
async function uploadFile(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showToast('Only image files are allowed', 'error');
        return;
    }
    
    // Show progress
    uploadProgress.classList.remove('hidden');
    const progressFill = uploadProgress.querySelector('.progress-fill');
    progressFill.style.width = '0%';
    
    // Animate progress
    setTimeout(() => {
        progressFill.style.transition = 'width 3s ease-in-out';
        progressFill.style.width = '70%';
    }, 100);
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Upload to server
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Upload failed');
        }
        
        // Complete progress
        progressFill.style.width = '100%';
        
        // Store session data
        sessionId = data.sessionId;
        extractedData = data.data;
        
        // Show success and transition to edit
        setTimeout(() => {
            showToast(data.message || 'Text extracted successfully!', 'success');
            generateEditForm();
            showSection('edit');
            uploadProgress.classList.add('hidden');
        }, 500);
        
    } catch (error) {
        console.error('Upload error:', error);
        showToast(error.message, 'error');
        uploadProgress.classList.add('hidden');
    }
}

/**
 * Generate edit form from extracted OCR data
 */
function generateEditForm() {
    editForm.innerHTML = '';
    currentFields = extractedData.fields;
    
    // Add text fields
    currentFields.forEach((field, index) => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = field.label;
        label.setAttribute('for', field.id);
        
        // Add confidence indicator if low
        if (field.confidence && field.confidence < 70) {
            const confBadge = document.createElement('span');
            confBadge.className = 'confidence-badge low';
            confBadge.textContent = ` (${field.confidence}% confidence)`;
            confBadge.style.cssText = 'color: #f59e0b; font-size: 0.75rem; font-weight: normal;';
            label.appendChild(confBadge);
        }
        
        const isMultiline = field.value.length > 100;
        const input = document.createElement(isMultiline ? 'textarea' : 'input');
        input.className = isMultiline ? 'form-textarea' : 'form-input';
        input.id = field.id;
        input.value = field.value;
        input.dataset.fieldIndex = index;
        
        if (!isMultiline) {
            input.type = 'text';
        }
        
        // Update field value on change
        input.addEventListener('input', (e) => {
            currentFields[index].value = e.target.value;
        });
        
        formGroup.appendChild(label);
        formGroup.appendChild(input);
        editForm.appendChild(formGroup);
    });
    
    // Add info message if no fields found
    if (currentFields.length === 0) {
        const noFieldsMsg = document.createElement('div');
        noFieldsMsg.className = 'no-fields-message';
        noFieldsMsg.style.cssText = 'text-align: center; padding: 40px; color: var(--text-muted);';
        noFieldsMsg.innerHTML = '<p>No text was detected in the image.</p><p>Please try uploading a clearer image with readable text.</p>';
        editForm.appendChild(noFieldsMsg);
    }
}

/**
 * Show preview section
 */
async function showPreview() {
    if (currentFields.length === 0) {
        showToast('No text fields to process', 'warning');
        return;
    }
    
    showLoading('Generating preview...');
    
    try {
        // Get preview warnings
        const response = await fetch(`${API_BASE_URL}/preview`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                fields: currentFields
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Preview generation failed');
        }
        
        // Display warnings if any
        const warningsContainer = document.getElementById('warningsContainer');
        if (data.warnings && data.warnings.length > 0) {
            warningsContainer.classList.remove('hidden');
            warningsContainer.innerHTML = `
                <div class="warning-title">⚠ OCR Warnings</div>
                <ul class="warning-list">
                    ${data.warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            `;
        } else {
            warningsContainer.classList.add('hidden');
        }
        
        hideLoading();
        showSection('preview');
        
    } catch (error) {
        console.error('Preview error:', error);
        showToast(error.message, 'error');
        hideLoading();
    }
}

/**
 * Download regenerated image
 */
async function downloadImage() {
    showLoading('Regenerating image...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/regenerate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                fields: currentFields
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Image regeneration failed');
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'image_edited.jpg';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        hideLoading();
        showToast('Image downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showToast(error.message, 'error');
        hideLoading();
    }
}

/**
 * Navigate back to edit section
 */
function backToEdit() {
    showSection('edit');
}

/**
 * Reset and upload new image
 */
async function resetUpload() {
    // Clear session on server
    if (sessionId) {
        try {
            await fetch(`${API_BASE_URL}/clear-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sessionId: sessionId })
            });
        } catch (error) {
            console.error('Clear session error:', error);
        }
    }
    
    // Reset state
    sessionId = null;
    extractedData = null;
    currentFields = [];
    fileInput.value = '';
    editForm.innerHTML = '';
    
    // Show upload section
    showSection('upload');
    showToast('Ready for new upload', 'success');
}

/**
 * Show specific section
 */
function showSection(section) {
    uploadSection.classList.remove('active');
    editSection.classList.remove('active');
    previewSection.classList.remove('active');
    
    uploadSection.classList.add('hidden');
    editSection.classList.add('hidden');
    previewSection.classList.add('hidden');
    
    if (section === 'upload') {
        uploadSection.classList.remove('hidden');
        uploadSection.classList.add('active');
    } else if (section === 'edit') {
        editSection.classList.remove('hidden');
        editSection.classList.add('active');
    } else if (section === 'preview') {
        previewSection.classList.remove('hidden');
        previewSection.classList.add('active');
    }
}

/**
 * Show loading overlay
 */
function showLoading(text = 'Processing...') {
    loadingOverlay.classList.remove('hidden');
    loadingOverlay.querySelector('.loading-text').textContent = text;
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => {
            if (toastContainer.contains(toast)) {
                toastContainer.removeChild(toast);
            }
        }, 300);
    }, 4000);
}
