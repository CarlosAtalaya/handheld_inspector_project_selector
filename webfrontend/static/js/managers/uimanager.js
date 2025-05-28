// uimanager.js
export class UIManager {
    constructor() {
        this.stateElements = document.querySelectorAll('[data-state]');
        this.sideElements = document.querySelectorAll('[data-side]');
        this.contentElements = document.querySelectorAll('[data-state-content]');

        // Add toggle UI/Report view event listener
        const guiContainer = document.querySelector('.gui-container');
        const a4Container = document.querySelector('.a4-container');
        const btnToggleReport = document.querySelector('.btn-toggle-report');
        const btnZoomContainer = document.querySelector('.zoom-btn-container');

        btnToggleReport.addEventListener('click', () => {
            guiContainer.classList.toggle('contracted');
            a4Container.classList.toggle('expanded');
            btnZoomContainer.classList.toggle('unhide');
        });
    }

    initialize() {
        this.updateUIForState({
            currentState: 'project_state',
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

        if (state.data?.project_data) {
            this._updateProjectData(state.data.project_data);
        }
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

    _updateProjectData(projectData) {
        
        const defectSelect = document.getElementById('defect-type');
        
        if (defectSelect && projectData.defects) {
            this._clearSelectOptions(defectSelect);
            defectSelect.innerHTML = '<option value="" disabled selected>DEFECT</option>';
            projectData.defects.forEach(defect => {
                const option = document.createElement('option');
                option.value = defect.toLowerCase();
                option.textContent = defect;
                defectSelect.appendChild(option);
            });
        }

        const qualitySelect = document.getElementById('surface-quality');
        
        if (qualitySelect && projectData.quality) {
            this._clearSelectOptions(qualitySelect);
            qualitySelect.innerHTML = '<option value="" disabled selected>(A/B/C)</option>';
            projectData.quality.forEach(quality => {
                const option = document.createElement('option');
                option.value = quality.toLowerCase();
                option.textContent = quality;
                qualitySelect.appendChild(option);
            });
        }

        const finishSelect = document.getElementById('finish');
        
        if (finishSelect && projectData.finish) {
            this._clearSelectOptions(finishSelect);
            finishSelect.innerHTML = '<option value="" disabled selected>(VISUAL/PAINTED)</option>';
            projectData.finish.forEach(finish => {
                const option = document.createElement('option');
                option.value = finish.toLowerCase();
                option.textContent = finish;
                finishSelect.appendChild(option);
            });
        }
    }

    _clearSelectOptions(selectElement) {
        while (selectElement.children.length > 1) {
            selectElement.removeChild(selectElement.lastChild);
        }
    }
}