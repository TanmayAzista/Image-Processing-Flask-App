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

registerUIAction('undo-btn', 'click', () => {
    fetch('/stack/undo', { method: 'POST' })
        .then(() => {
            ImageViewer.reload();   // GET /image
            return fetchStackState();
        });
});

registerUIAction('redo-btn', 'click', () => {
    fetch('/stack/redo', { method: 'POST' })
        .then(() => {
            ImageViewer.reload();   // GET /image
            return fetchStackState();
        });
});

function stackReset(){
    fetch('/stack', { method: 'DELETE' })
        .then(() => {
            ImageViewer.reload();   // clears viewer
            return fetchStackState();
        });
}

registerUIAction('reset-btn', 'click', () => {
    stackReset()
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
    
                thumbDiv.onclick = () => selectImage(img.uuid);
                // thumbDiv.onclick = () => ImageViewer.loadImage(img.uuid)
                // TODO: Add click handler to select image
                imageListContainer.appendChild(thumbDiv);
            });
        });
}

let stackState = null;
function fetchStackState() {
    return fetch('/stack/state')
        .then(res => res.json())
        .then(state => {
            stackState = state;
            updateUIState();
            return state;
        });
}

function updateUIState() {
    const imageList = document.getElementById('image-list-container');
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    const resetBtn = document.getElementById('reset-btn');

    if (!stackState) return;

    // Lock image selection if dirty
    imageList.style.pointerEvents = stackState.is_dirty ? 'none' : 'auto';
    imageList.style.opacity = stackState.is_dirty ? '0.5' : '1';

    undoBtn.disabled = !stackState.undo_possible;
    redoBtn.disabled = !stackState.redo_possible;
    resetBtn.disabled = !stackState.has_image;
}

function selectImage(uuid) {
    fetch(`/image?_uuid=${encodeURIComponent(uuid)}`, {
        method: 'PUT'
    })
    .then(res => {
        if (!res.ok) throw new Error("Image select failed");
        return ImageViewer.reload();
    })
    .then(() => fetchStackState())
    .catch(err => alert(err.message));
}


// Bind all registered actions on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    UIActionRegistry.bindAll();
    fetchAndRenderImageList();
    ImageViewer.init();     // Initialise Image Viewer
    fetchStackState()
    OpsUI.init();
    ImageViewer.reload()
});