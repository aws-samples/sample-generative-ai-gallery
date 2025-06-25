// Main application logic
class ImageGalleryApp {
    constructor() {
        this.currentPage = 1;
        this.currentFilters = {};
        this.selectMode = false;
        this.selectedImages = new Set();
        
        this.initializeElements();
        this.bindEvents();
        this.loadImages();
    }

    initializeElements() {
        // Get DOM elements
        this.elements = {
            loadingSpinner: document.getElementById('loadingSpinner'),
            alertContainer: document.getElementById('alertContainer'),
            filterForm: document.getElementById('filterForm'),
            activeFilters: document.getElementById('activeFilters'),
            filterBadges: document.getElementById('filterBadges'),
            imageCount: document.getElementById('imageCount'),
            imagesGrid: document.getElementById('imagesGrid'),
            pagination: document.getElementById('pagination'),
            selectModeBtn: document.getElementById('selectModeBtn'),
            selectionControls: document.getElementById('selectionControls'),
            selectAllBtn: document.getElementById('selectAllBtn'),
            deselectAllBtn: document.getElementById('deselectAllBtn'),
            deleteSelectedBtn: document.getElementById('deleteSelectedBtn'),
            resetFilters: document.getElementById('resetFilters'),
            clearAllFilters: document.getElementById('clearAllFilters')
        };
    }

    bindEvents() {
        // Filter form submission
        this.elements.filterForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });

        // Reset filters
        this.elements.resetFilters.addEventListener('click', () => {
            this.resetFilters();
        });

        // Clear all filters
        this.elements.clearAllFilters.addEventListener('click', () => {
            this.resetFilters();
        });

        // Selection mode toggle
        this.elements.selectModeBtn.addEventListener('click', () => {
            this.toggleSelectionMode();
        });

        // Selection controls
        this.elements.selectAllBtn.addEventListener('click', () => {
            this.selectAllImages();
        });

        this.elements.deselectAllBtn.addEventListener('click', () => {
            this.deselectAllImages();
        });

        this.elements.deleteSelectedBtn.addEventListener('click', () => {
            this.deleteSelectedImages();
        });
    }

    showLoading() {
        this.elements.loadingSpinner.style.display = 'block';
    }

    hideLoading() {
        this.elements.loadingSpinner.style.display = 'none';
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        this.elements.alertContainer.appendChild(alertDiv);

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    async loadImages() {
        try {
            this.showLoading();
            
            const params = {
                page: this.currentPage,
                per_page: APP_CONFIG.DEFAULT_PER_PAGE,
                ...this.currentFilters
            };

            const response = await api.fetchImages(params);
            
            if (response.success) {
                this.renderImages(response.images);
                this.renderPagination(response.pagination);
                this.updateImageCount(response.pagination);
                this.populateFilterOptions(response.filter_options);
                this.updateActiveFilters(response.current_filters);
            } else {
                this.showAlert('Error loading images: ' + response.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error loading images: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }

    renderImages(images) {
        this.elements.imagesGrid.innerHTML = '';
        
        images.forEach((image, index) => {
            const imageCard = this.createImageCard(image, index);
            this.elements.imagesGrid.appendChild(imageCard);
        });
    }

    createImageCard(image, index) {
        const col = document.createElement('div');
        col.className = 'col';
        
        const metadata = image.metadata || {};
        const metadataHtml = Object.keys(metadata).length > 0 ? `
            <div class="metadata">
                <p class="mb-1"><strong>Historical Period:</strong> ${metadata.historical_period || 'N/A'}</p>
                <p class="mb-1"><strong>Gender:</strong> ${metadata.gender || 'N/A'}</p>
                <p class="mb-1"><strong>Skin Tone:</strong> ${metadata.skin_tone || 'N/A'}</p>
                <p class="mb-1"><strong>Profession:</strong> ${metadata.profession || 'N/A'}</p>
                <p class="mb-0"><strong>Artistic Style:</strong> ${metadata.artistic_style || 'N/A'}</p>
            </div>
        ` : '';

        col.innerHTML = `
            <div class="card h-100 card-container" data-key="${image.key}">
                <input type="checkbox" class="image-checkbox" style="display: none;" data-key="${image.key}">
                <a href="detail.html?key=${encodeURIComponent(image.key)}" class="image-link">
                    <img src="${image.url}" class="card-img-top" alt="Generated Image">
                </a>
                <div class="card-body">
                    <h5 class="card-title">Image #${((this.currentPage - 1) * APP_CONFIG.DEFAULT_PER_PAGE) + index + 1}</h5>
                    ${metadataHtml}
                </div>
            </div>
        `;

        // Add click handler for selection mode
        const card = col.querySelector('.card');
        card.addEventListener('click', (e) => {
            if (this.selectMode) {
                e.preventDefault();
                const checkbox = card.querySelector('.image-checkbox');
                checkbox.checked = !checkbox.checked;
                this.updateSelectedImages();
            }
        });

        return col;
    }

    renderPagination(pagination) {
        this.elements.pagination.innerHTML = '';
        
        if (pagination.total_pages <= 1) return;

        // Previous button
        if (pagination.page > 1) {
            const prevLi = document.createElement('li');
            prevLi.className = 'page-item';
            prevLi.innerHTML = `<a class="page-link" href="#" data-page="${pagination.page - 1}">&laquo;</a>`;
            this.elements.pagination.appendChild(prevLi);
        }

        // Page numbers
        for (let i = 1; i <= pagination.total_pages; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === pagination.page ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
            this.elements.pagination.appendChild(pageLi);
        }

        // Next button
        if (pagination.page < pagination.total_pages) {
            const nextLi = document.createElement('li');
            nextLi.className = 'page-item';
            nextLi.innerHTML = `<a class="page-link" href="#" data-page="${pagination.page + 1}">&raquo;</a>`;
            this.elements.pagination.appendChild(nextLi);
        }

        // Add click handlers
        this.elements.pagination.addEventListener('click', (e) => {
            e.preventDefault();
            if (e.target.classList.contains('page-link')) {
                const page = parseInt(e.target.dataset.page);
                if (page && page !== this.currentPage) {
                    this.currentPage = page;
                    this.loadImages();
                }
            }
        });
    }

    updateImageCount(pagination) {
        const isFiltered = Object.keys(this.currentFilters).some(key => this.currentFilters[key]);
        const prefix = isFiltered ? 'Filtered Results:' : 'Total:';
        this.elements.imageCount.textContent = `${prefix} ${pagination.total_images} images, Page ${pagination.page}/${pagination.total_pages}`;
    }

    populateFilterOptions(filterOptions) {
        // Populate filter dropdowns
        Object.keys(filterOptions).forEach(filterType => {
            const selectElement = document.getElementById(filterType.slice(0, -1)); // Remove 's' from end
            if (selectElement) {
                // Clear existing options except "All"
                selectElement.innerHTML = '<option value="">All</option>';
                
                // Add new options
                filterOptions[filterType].forEach(option => {
                    const optionElement = document.createElement('option');
                    optionElement.value = option;
                    optionElement.textContent = option;
                    if (this.currentFilters[filterType.slice(0, -1)] === option) {
                        optionElement.selected = true;
                    }
                    selectElement.appendChild(optionElement);
                });
            }
        });
    }

    updateActiveFilters(currentFilters) {
        const activeFilters = [];
        
        Object.keys(currentFilters).forEach(key => {
            if (currentFilters[key]) {
                const label = key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                activeFilters.push(`${label}: ${currentFilters[key]}`);
            }
        });

        if (activeFilters.length > 0) {
            this.elements.filterBadges.innerHTML = activeFilters
                .map(filter => `<span class="badge bg-primary me-2">${filter}</span>`)
                .join('');
            this.elements.activeFilters.style.display = 'block';
        } else {
            this.elements.activeFilters.style.display = 'none';
        }
    }

    applyFilters() {
        const formData = new FormData(this.elements.filterForm);
        this.currentFilters = {};
        
        for (let [key, value] of formData.entries()) {
            if (value) {
                this.currentFilters[key] = value;
            }
        }
        
        this.currentPage = 1; // Reset to first page
        this.loadImages();
    }

    resetFilters() {
        this.elements.filterForm.reset();
        this.currentFilters = {};
        this.currentPage = 1;
        this.loadImages();
    }

    toggleSelectionMode() {
        this.selectMode = !this.selectMode;
        
        const checkboxes = document.querySelectorAll('.image-checkbox');
        const imageLinks = document.querySelectorAll('.image-link');
        
        if (this.selectMode) {
            this.elements.selectModeBtn.textContent = 'Exit Selection Mode';
            this.elements.selectModeBtn.classList.remove('btn-outline-primary');
            this.elements.selectModeBtn.classList.add('btn-primary');
            this.elements.selectionControls.style.display = 'block';
            
            checkboxes.forEach(checkbox => checkbox.style.display = 'block');
            imageLinks.forEach(link => link.style.pointerEvents = 'none');
        } else {
            this.elements.selectModeBtn.textContent = 'Selection Mode';
            this.elements.selectModeBtn.classList.remove('btn-primary');
            this.elements.selectModeBtn.classList.add('btn-outline-primary');
            this.elements.selectionControls.style.display = 'none';
            
            checkboxes.forEach(checkbox => {
                checkbox.style.display = 'none';
                checkbox.checked = false;
            });
            imageLinks.forEach(link => link.style.pointerEvents = 'auto');
            
            this.selectedImages.clear();
        }
    }

    selectAllImages() {
        const checkboxes = document.querySelectorAll('.image-checkbox');
        checkboxes.forEach(checkbox => checkbox.checked = true);
        this.updateSelectedImages();
    }

    deselectAllImages() {
        const checkboxes = document.querySelectorAll('.image-checkbox');
        checkboxes.forEach(checkbox => checkbox.checked = false);
        this.updateSelectedImages();
    }

    updateSelectedImages() {
        this.selectedImages.clear();
        const checkedBoxes = document.querySelectorAll('.image-checkbox:checked');
        checkedBoxes.forEach(checkbox => {
            this.selectedImages.add(checkbox.dataset.key);
        });
    }

    async deleteSelectedImages() {
        if (this.selectedImages.size === 0) {
            this.showAlert('Please select images to delete.', 'warning');
            return;
        }

        if (!confirm(`Are you sure you want to delete ${this.selectedImages.size} selected images?`)) {
            return;
        }

        try {
            this.showLoading();
            const response = await api.deleteMultipleImages(Array.from(this.selectedImages));
            
            if (response.success) {
                this.showAlert(response.message, 'success');
                this.selectedImages.clear();
                this.toggleSelectionMode(); // Exit selection mode
                this.loadImages(); // Reload images
            } else {
                this.showAlert('Error deleting images: ' + response.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error deleting images: ' + error.message, 'danger');
        } finally {
            this.hideLoading();
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ImageGalleryApp();
});
