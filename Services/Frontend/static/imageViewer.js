// imageViewer.js
// Responsible ONLY for rendering, panning, zooming a single image

const ImageViewer = (function () {
    let imageElement = null;
    let containerElement = null;
    let viewerElement = null;

    let currentUUID = null;

    // Transform state
    let scale = 1;
    let translateX = 0;
    let translateY = 0;

    // Drag state
    let isDragging = false;
    let lastMouseX = 0;
    let lastMouseY = 0;

    function init() {
        viewerElement = document.getElementById("image-viewer");
        containerElement = document.getElementById("image-container");
        imageElement = document.getElementById("main-image");

        if (!viewerElement || !containerElement || !imageElement) {
            console.error("ImageViewer init failed: DOM elements missing");
            return;
        }

        attachInteractionHandlers();
    }

    function loadImage(uuid) {
        currentUUID = uuid;

        imageElement.onload = () => fitImageToView();
        imageElement.src = `/image?_uuid=${encodeURIComponent(uuid)}`;
    }

    function reload() {
        imageElement.onload = () => fitImageToView();
        imageElement.src = `/image?ts=${Date.now()}`;
    }

    function fitImageToView() {
        const viewWidth = viewerElement.clientWidth;
        const viewHeight = viewerElement.clientHeight;

        const imgWidth = imageElement.naturalWidth;
        const imgHeight = imageElement.naturalHeight;

        const scaleX = viewWidth / imgWidth;
        const scaleY = viewHeight / imgHeight;

        scale = Math.min(scaleX, scaleY, 1);

        translateX = -imgWidth * scale / 2;
        translateY = -imgHeight * scale / 2;

        updateTransform();
    }

    function updateTransform() {
        containerElement.style.transform =
            `translate(${translateX}px, ${translateY}px) scale(${scale})`;
    }

    function attachInteractionHandlers() {
        // Zoom
        containerElement.addEventListener("wheel", handleZoom, { passive: false });

        // Pan
        containerElement.addEventListener("mousedown", handleMouseDown);
        window.addEventListener("mousemove", handleMouseMove);
        window.addEventListener("mouseup", handleMouseUp);
    }

    function handleZoom(event) {
        // if (!currentUUID) return;

        event.preventDefault();

        const rect = containerElement.getBoundingClientRect();
        const offsetX = event.clientX - rect.left;
        const offsetY = event.clientY - rect.top;

        const zoomFactor = 1.1;
        const direction = event.deltaY < 0 ? 1 : -1;
        const zoom = Math.pow(zoomFactor, direction);

        translateX -= offsetX * (zoom - 1);
        translateY -= offsetY * (zoom - 1);

        scale *= zoom;
        scale = Math.max(0.01, scale);

        updateTransform();
    }

    function handleMouseDown(event) {
        // if (!currentUUID) return;

        isDragging = true;
        lastMouseX = event.clientX;
        lastMouseY = event.clientY;
    }

    function handleMouseMove(event) {
        if (!isDragging) return;

        translateX += event.clientX - lastMouseX;
        translateY += event.clientY - lastMouseY;

        lastMouseX = event.clientX;
        lastMouseY = event.clientY;

        updateTransform();
    }

    function handleMouseUp() {
        isDragging = false;
    }

    // Public API
    return {
        init,
        reload
    };
})();
