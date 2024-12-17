class FeaturedImageUploader {
    constructor(imageFieldId, bannerFieldId) {
        this.imageField = document.getElementById(imageFieldId);
        this.bannerField = document.getElementById(bannerFieldId);
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Setup drag and drop for both fields
        [this.imageField, this.bannerField].forEach(field => {
            if (field) {
                field.parentElement.addEventListener('dragover', this.handleDragOver.bind(this));
                field.parentElement.addEventListener('drop', (e) => this.handleDrop(e, field));
            }
        });

        // Setup paste event on document
        document.addEventListener('paste', this.handlePaste.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        e.dataTransfer.dropEffect = 'copy';
    }

    async handleDrop(e, field) {
        e.preventDefault();
        e.stopPropagation();

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                await this.handleImageFile(file, field);
            }
        }
    }

    async handlePaste(e) {
        const items = (e.clipboardData || e.originalEvent.clipboardData).items;
        for (const item of items) {
            if (item.type.indexOf('image') === 0) {
                const file = item.getAsFile();
                // Default to image field for paste
                await this.handleImageFile(file, this.imageField);
                break;
            }
        }
    }

    async handleImageFile(file, field) {
        // Create a preview if needed
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = field.parentElement.querySelector('.image-preview');
            if (preview) {
                preview.src = e.target.result;
            }
        };
        reader.readAsDataURL(file);

        // Create a new file input
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        field.files = dataTransfer.files;
        
        // Trigger change event
        field.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FeaturedImageUploader('id_featured_image-0-image', 'id_featured_image-0-banner');
});
