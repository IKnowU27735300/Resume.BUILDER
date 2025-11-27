/**
 * Resume Builder - Frontend Application Logic
 * Handles file upload, form generation, and API communication
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
let sessionId = null;
let parsedData = null;
let currentFields = [];
let currentImages = [];

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
    if (file && file.type === 'application/pdf') {
        uploadFile(file);
    } else {
        showToast('Please upload a PDF file', 'error');
    }
}

/**
 * Upload file to server
 */
async function uploadFile(file) {
    // Validate file
    if (file.size > 5 * 1024 * 1024) {
        showToast('File size exceeds 5 MB limit', 'error');
        return;
    }
    
    if (file.type !== 'application/pdf') {
        showToast('Only PDF files are allowed', 'error');
        return;
    }
    
    // Show progress
    uploadProgress.classList.remove('hidden');
    const progressFill = uploadProgress.querySelector('.progress-fill');
    progressFill.style.width = '0%';
    
    // Animate progress
    setTimeout(() => {
        progressFill.style.transition = 'width 2s ease-in-out';
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
        parsedData = data.data;
        
        // Show success and transition to edit
        setTimeout(() => {
            showToast('Resume parsed successfully!', 'success');
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
 * Generate edit form from parsed data
 */
function generateEditForm() {
    editForm.innerHTML = '';
    currentFields = parsedData.fields;
    currentImages = parsedData.images;
    
    // Add text fields
    currentFields.forEach((field, index) => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = field.label;
        label.setAttribute('for', field.id);
        
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
    
    // Add image upload fields
    currentImages.forEach((image, index) => {
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group';
        
        const imageGroup = document.createElement('div');
        imageGroup.className = 'image-upload-group';
        
        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = `Image ${index + 1} - Replace (Optional)`;
        
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = 'image/*';
        input.className = 'form-input';
        input.dataset.imageIndex = index;
        
        // Preview current image
        const preview = document.createElement('img');
        preview.className = 'image-preview';
        preview.src = `data:image/${image.format};base64,${image.data}`;
        preview.alt = `Image ${index + 1}`;
        
        // Handle image replacement
        input.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    const base64 = event.target.result.split(',')[1];
                    currentImages[index].data = base64;
                    preview.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
        
        imageGroup.appendChild(label);
        imageGroup.appendChild(input);
        imageGroup.appendChild(preview);
        formGroup.appendChild(imageGroup);
        editForm.appendChild(formGroup);
    });
}

/**
 * Show preview section
 */
async function showPreview() {
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
                fields: currentFields,
                images: currentImages
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Preview generation failed');
        }
        
        // Display warnings if any
        const warningsContainer = document.getElementById('warningsContainer');
        if (data.fontWarnings && data.fontWarnings.length > 0) {
            warningsContainer.classList.remove('hidden');
            warningsContainer.innerHTML = `
                <div class="warning-title">⚠ Font Substitutions</div>
                <ul class="warning-list">
                    ${data.fontWarnings.map(w => `<li>${w}</li>`).join('')}
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
 * Download PDF
 */
async function downloadPDF() {
    showLoading('Generating PDF...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/regenerate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                fields: currentFields,
                images: currentImages
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'PDF generation failed');
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume_edited.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        hideLoading();
        showToast('PDF downloaded successfully!', 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showToast(error.message, 'error');
        hideLoading();
    }
}

/**
 * Download DOCX
 */
async function downloadDOCX() {
    showLoading('Generating DOCX...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/export-docx`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sessionId: sessionId,
                fields: currentFields,
                images: currentImages
            })
        });
        
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'DOCX generation failed');
        }
        
        // Download file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'resume_edited.docx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        hideLoading();
        showToast('DOCX downloaded successfully!', 'success');
        
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
 * Reset and upload new resume
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
    parsedData = null;
    currentFields = [];
    currentImages = [];
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
            toastContainer.removeChild(toast);
        }, 300);
    }, 4000);
}
