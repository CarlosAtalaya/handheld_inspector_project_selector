// app.js
import { statemanager } from "./managers/statemanager.js";
import { UIManager } from "./managers/uimanager.js";
import { ScreenManager } from "./managers/screenmanager.js";
import { ReportManager } from "./managers/reportmanager.js";

let selectedDefect = null;

// Initialize Screen Manager and subscribe to event changes
const screenManager = new ScreenManager();
screenManager.initialize();
statemanager.subscribe(state => {screenManager.updateScreenForState(state)})

// Initialize UI Manager and subscribe to event changes
const uiManager = new UIManager();
uiManager.initialize();
statemanager.subscribe(state => {
    uiManager.updateUIForState(state);
});

// Initialize Report Manager and subscribe to event changes
const reportManager = new ReportManager('template.html');
reportManager.initialize();
statemanager.subscribe(state => {
    reportManager.updateReportForState(state)
});


const btnCaptureFrame = document.getElementById('btn-capture-frame');
btnCaptureFrame.addEventListener('click', function () { handleCaptureClick.call(this, 'capture'); });

const btnYes = document.getElementById('btn-yes');
btnYes.addEventListener('click', function() { handleCaptureClick.call(this, 'yes'); });

const btnNo = document.getElementById('btn-no');
btnNo.addEventListener('click', function() { handleCaptureClick.call(this, 'no'); });

const btnRepeat = document.getElementById('btn-repeat');
btnRepeat.addEventListener('click', function () { handleCaptureClick.call(this, 'repeat'); });

const btnKeep = document.getElementById('btn-keep');
btnKeep.addEventListener('click', function () { handleCaptureClick.call(this, 'keep'); });

const btnDrop = document.getElementById('btn-drop');
btnDrop.addEventListener('click', function () { handleCaptureClick.call(this, 'drop'); });

const btnMore = document.getElementById('btn-more');
btnMore.addEventListener('click', function () { handleCaptureClick.call(this, 'more'); });

const btnNewPart = document.getElementById('btn-new-part');
btnNewPart.addEventListener('click', function () { handleCaptureClick.call(this, 'new-part'); });

const btnNewProject = document.getElementById('btn-new-project');
btnNewProject.addEventListener('click', function () { handleCaptureClick.call(this, 'new-project'); });

const btnPrint = document.getElementById('btn-print');
btnPrint.addEventListener('click', function () {
    window.print();  // Show print dialog
    handleCaptureClick.call(this, 'print');
});


document.querySelectorAll(".btn-deffect").forEach((button) => {
    button.addEventListener("click", function (event) {
        selectedDefect = event.target.id;
        handleCaptureClick.call(this, '');
    });
});

// FILL PROJECT AND INSPECTOR form submit
const btnOkProject = document.getElementById('btn-ok-project');
btnOkProject.addEventListener('click', function () {
    const projectForm = document.getElementById('project-inspector-form');
    const project = document.getElementById('project').value;
    const inspector = document.getElementById('inspector').value;
    
    if (project && inspector) {
        document.getElementById('project').value = '';
        document.getElementById('inspector').value = '';
        
        handleCaptureClick.call(this, '', {
            project: project,
            inspector: inspector
        });
    } else {
        if (!project) document.getElementById('project').style.borderColor = 'red';
        if (!inspector) document.getElementById('inspector').style.borderColor = 'red';

        setTimeout(() => {
            document.getElementById('project').style.borderColor = '';
            document.getElementById('inspector').style.borderColor = '';
        }, 2000);
    }
});

// STANDBY form submit
const formSubmit = document.getElementById('standby-form');
formSubmit.addEventListener('submit', function(e) {
    e.preventDefault()  // prevent default for submission
    const formData = new FormData(this);

    // Get values
    const partNumber = formData.get('partnumber')?.trim();
    const serialNumber = formData.get('serialnumber')?.trim();

    if (partNumber && serialNumber) {
        e.target.reset();  // clear form on advance
    }

    // Keys should match with template.html classes (or later modified in backend)
    handleCaptureClick.call(this, '', {'inspected-part': partNumber, 'serial-number': serialNumber});
});

// DEFECT SELECTION form submit
const defectFormSubmit = document.getElementById('defect-selection-form');
defectFormSubmit.addEventListener('submit', function(e) {
    e.preventDefault();  // Prevent default form submission
    const formData = new FormData(this);

    const defectType = formData.get('defect-type');
    selectedDefect = defectType;
    const surfaceQuality = formData.get('surface-quality');
    const finish = formData.get('finish');

    const fullDefect = `${defectType} - ${surfaceQuality} - ${finish}`;

    handleCaptureClick.call(this, '', {
        // Criteria state data
        'defect-type': defectType,
        'surface-quality': surfaceQuality,
        'finish': finish,
        // Report data
        'defect-name': fullDefect.toUpperCase()
    });
});


async function handleCaptureClick(action, data={}) {
    this.disabled = true;
    this.classList.add('loading');
    const success = await statemanager.transitionState({
        action: action,
        selectedDefect: selectedDefect,
        data: data,
    })
    this.disabled = false;
    this.classList.remove('loading');

    if (!success) {
        // TODO: Handle Error
    }
}
