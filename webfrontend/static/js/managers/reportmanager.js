// reportmanager.js
import { ZoomController } from "../utils/zoom.js";

export class ReportManager {
    constructor(templateName, statemanager) {
        this.templatePath = `static/templates/${templateName}`
        this.a4Document = document.querySelector('.a4-document');
        this.a4Template = null;
        this.statemanager = statemanager;

        // Init Zoom Controller
        this.ZoomController = new ZoomController(".a4-document", ".btn-zoom-in", ".btn-zoom-out");

        // Add Edit Mode 
        this.editMode = false;
        document.getElementById('btn-edit').addEventListener('click', () => {
            // toggle edit mode
            this.editMode = !this.editMode;
            // toggle delete buttons activation
            const deleteButtons = document.querySelectorAll('.btn-a4-delete');
            deleteButtons.forEach(btn => { btn.classList.toggle('active'); })
        })
    }

    async initialize() {
        try {
            this.a4Template = await this.getReportTemplate();
            this.addPage(1);
        } catch (error) {
            console.error('Failed to init report manager:', error)
        }
    }

    async getReportTemplate() {
        // Fetch HTML
        const response = await fetch(this.templatePath);
        const html = await response.text();

        // Parse HTML content
        const parser = new DOMParser();
        const indexDoc = parser.parseFromString(html, 'text/html');

        // Find template
        const a4Page = indexDoc.querySelector('.a4-page');

        return a4Page
    }

    addPage(pageNumber) {
        const a4PageClone = this.a4Template.cloneNode(true);
        a4PageClone.id = `a4-page-${pageNumber}`;

        // Create remove btn for page
        const deleteBtn = this.addRemoveButton(pageNumber);
        if (this.editMode) { deleteBtn.classList.toggle('active'); }
        // Append button to the page
        a4PageClone.appendChild(deleteBtn);

        // this.a4Document.appendChild(a4PageClone);
        this.a4Document.prepend(a4PageClone); // add new page at top of document
        return a4PageClone
    }

    addRemoveButton(pageNumber) {
        // Get and clone delete button template
        const buttonTemplate = document.getElementById('delete-btn-template');
        const deleteBtn = buttonTemplate.content.cloneNode(true).firstElementChild;
        deleteBtn.addEventListener('click', () => {
            // Report backend
            const payload = {
                action: 'delete_page',
                data: {
                    'n_page': pageNumber
                }
            }
            this.statemanager.transitionState(payload, '/actions/delete_page')
        });

        return deleteBtn
    }

    getPage(pageNumber) {
        return document.getElementById(`a4-page-${pageNumber}`);
    }

    removePage(pageNumber=-1) {
        const pages = this.a4Document.getElementsByClassName('a4-page');
        pages[pageNumber === -1 ? 0 : pages.length - pageNumber]?.remove(); // pages are in reverse order, 0 is last
    }

    cleanPages() {
        const pages = this.a4Document.getElementsByClassName('a4-page');
        while (pages.length > 0) {
            pages[0].remove();
        }
    }

    renumberPages(n_page) {
        const pages = this.a4Document.getElementsByClassName('a4-page');
        for (let i = 0; i < (pages.length + 1 - n_page); i++) {
            // Compute new page number and update id
            const newPageNumber = pages.length - i
            pages[i].id = `a4-page-${newPageNumber}`;
            
            // Update all references to page number on the page
            const pageNumberElements = pages[i].querySelectorAll('.fill-page-number');
            pageNumberElements.forEach(el => { el.textContent = newPageNumber; })
        }
    }

    isNonEmptyReport(report) {
        return !!(
            report && (
                Object.keys(report.images || {}).length ||
                Object.keys(report.text || {}).length)
        );
    }

    updateReportForState(state) {

        if (state.actions?.report) {
            const reportActions = state.actions.report;
            
            // Remove all pages
            if (reportActions.remove_all) {
                this.cleanPages();
            }
            // Remove page
            if (reportActions.remove_page) {
                this.removePage(reportActions.page_number);
            }
            // Add page
            if (reportActions.add_page) {
                this.addPage(reportActions.page_number);
            }
            // Renumber pages
            if (reportActions.renumber_pages) {
                this.renumberPages(state.data.report.page_number);
            }

            // Update content
            if (reportActions.update_page && this.isNonEmptyReport(state.data?.report)) {
                const pageNumber = state.data.n_inspection;
                const a4Page = this.getPage(pageNumber);

                if (state.data.report.text) {
                    Object.entries(state.data.report.text).forEach(([key, value]) => {
                        this.updateText(key, value, a4Page);
                    })
                }
                if (state.data.report.images) {
                    Object.entries(state.data.report.images).forEach(([key, value]) => {
                        this.updateImage(key, value, a4Page);
                    })
                }
            }
        }
    }

    updateText(className, text, container) {
        const elements = container.querySelectorAll(`.fill-${className}`);
        elements.forEach(el => el.textContent = text);
    }

    updateImage(className, src, container) {
        const elements = container.querySelectorAll(`.fill-${className}`);
        elements.forEach(el => el.src = src);
    }
}
