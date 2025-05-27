export class ZoomController {
    constructor(a4Selector, zoomInSelector, zoomOutSelector) {
        this.a4Document = document.querySelector(a4Selector);
        this.btnZoomIn = document.querySelector(zoomInSelector);
        this.btnZoomOut = document.querySelector(zoomOutSelector);
        this.zoomLevel = 1;
        this.zoomStep = 0.1;

        // A4 dimensions in pixels (assuming 96 DPI)
        this.a4Width = 210 * (96 / 25.4); // Convert mm to px (1 inch = 25.4mm, 1 inch = 96px)
        this.a4Height = 297 * (96 / 25.4);
        this.padding = 56;
        this.mediaMaxWidth = 800;  // needs to match css max-width media query

        // Event Listeners
        this.btnZoomIn.addEventListener("click", () => this.zoomIn());
        this.btnZoomOut.addEventListener("click", () => this.zoomOut());

        // Initialize Zoom on Page Load
        window.onload = () => this.setInitialZoom();
        // Reset zoom on window resize (Add Throttle if responsiveness seems degraded)
        window.addEventListener('resize', () => {this.setInitialZoom();})

    }

    setInitialZoom() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // Downscale by half it the report occupies just half the screen
        const downscale = (viewportWidth <= this.mediaMaxWidth) ? 1 : 2;

        // Calculate scale factor to fit half the website's width or height
        const scaleX = (viewportWidth / downscale) / (this.a4Width + this.padding);
        const scaleY = viewportHeight / this.a4Height;

        // Choose the smaller scale factor to maintain aspect ratio
        // this.zoomLevel = Math.min(scaleX, scaleY);
        this.zoomLevel = scaleX;

        this.applyZoom();
    }

    zoomIn() {
        this.zoomLevel += this.zoomStep;
        this.applyZoom();
    }

    zoomOut() {
        if (this.zoomLevel > 0.5) {
            this.zoomLevel -= this.zoomStep;
            this.applyZoom();
        }
    }

    applyZoom() {
        this.a4Document.style.transform = `scale(${this.zoomLevel})`;
        this.a4Document.style.transformOrigin = "top left"; // Ensure scaling from top-left
    }
}
