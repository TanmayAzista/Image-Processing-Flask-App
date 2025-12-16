// UI Action Registry Standard
// Usage: registerUIAction('elementId', 'event', handlerFn)
// Example: registerUIAction('my-btn', 'click', () => {...})

const UIActionRegistry = {
    actions: [],
    register: function(id, event, handler) {
        this.actions.push({id, event, handler});
    },
    bindAll: function() {
        this.actions.forEach(({id, event, handler}) => {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener(event, handler);
            }
        });
    }
};

// Helper to register UI actions
function registerUIAction(id, event, handler) {
    UIActionRegistry.register(id, event, handler);
}

// Example: Upload button and file input
registerUIAction('upload-btn', 'click', function() {
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.click();
});

registerUIAction('file-input', 'change', function() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    fetch('/upload', {
        method: 'PUT',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        fetchAndRenderImageList();
        console.log("Uploaded", data.uuid)
        // alert('Upload successful!');
        // TODO: update image list
    })
    .catch(err => {
        alert('Upload failed.');
    });
});

// Fetch and render image list with thumbnails
function fetchAndRenderImageList() {
    fetch('/api/images')
        .then(res => res.json())
        .then(images => {
            const imageListContainer = document.getElementById('image-list-container');
            if (!imageListContainer) return;
            imageListContainer.innerHTML = '';
            if (!images.length) {
                imageListContainer.innerHTML = '<div style="color: #888;">No images uploaded.</div>';
                return;
            }
            images.forEach(img => {
                const thumbDiv = document.createElement('div');
                thumbDiv.className = 'thumb-item';
                // Fetch thumbnail from backend (returns Bytes Stream)
                const imgEl = document.createElement('img');
                imgEl.src = `/image/thumbnail?_uuid=${encodeURIComponent(img.uuid)}`;
                imgEl.alt = 'thumb';
                imgEl.loading = 'lazy';

                const label = document.createElement('span');
                label.className = 'thumb-label';
                label.textContent = img.filename;

                thumbDiv.appendChild(imgEl);
                thumbDiv.appendChild(label);
                thumbDiv.onclick = () => ImageViewer.loadImage(img.uuid)
                // TODO: Add click handler to select image
                imageListContainer.appendChild(thumbDiv);
            });
        });
}

// Bind all registered actions on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    UIActionRegistry.bindAll();
    fetchAndRenderImageList();
    ImageViewer.init();     // Initialise Image Viewer
});