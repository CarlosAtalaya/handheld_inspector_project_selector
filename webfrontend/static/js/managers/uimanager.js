// uimanager.js
export class UIManager {
    constructor() {
        this.stateElements = document.querySelectorAll('[data-state]');
        this.sideElements = document.querySelectorAll('[data-side]');
        this.contentElements = document.querySelectorAll('[data-state-content]');
        this.selectElements = document.querySelectorAll('[data-state-select]');

        // Add toggle UI/Report view event listener
        const guiContainer = document.querySelector('.gui-container');
        const a4Container = document.querySelector('.a4-container');
        const infoContainer = document.querySelector('.info-container');
        const btnToggleReport = document.querySelector('.btn-toggle-report');
        const btnZoomContainer = document.querySelector('.zoom-btn-container');
        const btnEditContainer = document.querySelector('.edit-btn-container');
        const btnInfo = document.getElementById('btn-info');
        const btnCloseInfo = document.getElementById('btn-close-info');

        btnToggleReport.addEventListener('click', () => {
            guiContainer.classList.toggle('contracted');
            a4Container.classList.toggle('expanded');
            btnZoomContainer.classList.toggle('unhide');
            btnEditContainer.classList.toggle('unhide');
            infoContainer.classList.toggle('hide');
        });


        btnInfo.addEventListener('click', () => { infoContainer.classList.toggle('active'); });
        btnCloseInfo.addEventListener('click', () => { infoContainer.classList.toggle('active'); });
    }

    initialize() {
        this.updateUIForState({
            currentState: 'inspector_state',
            data: null
        });
    }

    resetFormsForState(currentState) {
        const form = document.querySelector(`[data-state="${currentState}"] form`);
        if (form) {
            form.reset();

            // Restore elements using data-reset
            form.querySelectorAll('[data-reset]').forEach(el => {
                const resetType = el.dataset.reset;

                if (resetType === 'show') {
                    // Remove hidden
                    el.classList.remove('hidden');
                } else if (resetType.startsWith('text:')) {
                    // Set default text
                    const defaultText = resetType.split(':')[1];
                    el.textContent = this.getDefaultText(defaultText);
                }
            });
        }
    }

    getDefaultText(key) {
        const textDefaults = {
            'default-criteria': 'Is that a defect according to quality criteria?',
        };
        return textDefaults[key] || '';
    }

    updateUIForState(state) {
        this._toggleStateElements(state.currentState);
        this._toggleSideElements(state.currentState, state.data?.guideline_side);
        this._updateContent(state);
        this._updateSelectsFromState(state);
    }

    _toggleStateElements(state) {
         // Update visibility based on state
        this.stateElements.forEach(element => {
            const states = element.dataset.state.split(' ');
            element.classList.toggle('active', states.includes(state));
        });
    }

    _toggleSideElements(state, side) {
        // Update visibility based on state and side
        this.sideElements.forEach(element => {
            const states = element.dataset.state.split(' ');
            if (states.includes(state)) {
                const element_side = element.dataset.side;
                element.classList.toggle('active', side === element_side);
            }
        })
    }

    _updateContent(state) {
         // Update content based on state data
        this.contentElements.forEach(element => {
            const contentKey = element.dataset.stateContent;
            element.textContent = state.data?.['ui-content']?.[contentKey] || '';
        });
    }

    _updateSelectsFromState(state) {
        const selectData = state.data?.select || {};
        this.selectElements.forEach(select => {
            const key = select.dataset.stateSelect;
            const values = selectData[key];
            if (Array.isArray(values)) {
                // Create dynamic placeholder
                const label = key.replace(/-/g, ' ').toUpperCase();
                const placeholder = document.createElement('option');
                placeholder.value = '';
                placeholder.disabled = true;
                placeholder.selected = true;
                placeholder.textContent = `SELECT ${label}`;
                // Clear existing options and add placeholder
                select.innerHTML = '';
                select.appendChild(placeholder);
                // Add new options
                values.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.toLowerCase();
                    option.textContent = item;
                    select.appendChild(option);
                });
            }
        });
    }
}