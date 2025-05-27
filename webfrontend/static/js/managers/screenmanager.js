// screenmanager.js
export class ScreenManager {
    constructor() {
        this.display = document.querySelector('.video-input');
    }

    initialize() {
        this.updateScreenForState({
            data: { screen: "/video_feed" }
        })
    }

    updateScreenForState(state) {
        const mediaSource = state.data?.screen;
        if (mediaSource) this.display.src = mediaSource;
    }
}