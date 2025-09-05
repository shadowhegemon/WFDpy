/**
 * WFD Logger Keyboard Shortcuts System
 * Provides rapid logging shortcuts for contest operations
 */

class WFDKeyboardShortcuts {
    constructor() {
        this.shortcuts = new Map();
        this.isEnabled = true;
        this.helpModalVisible = false;
        
        // Initialize shortcuts
        this.initializeShortcuts();
        
        // Bind event listeners
        this.bindEvents();
        
        // Show shortcuts in form labels
        this.addShortcutHints();
        
        console.log('WFD Keyboard Shortcuts initialized');
    }
    
    initializeShortcuts() {
        // Navigation shortcuts (global)
        this.addShortcut('Alt+H', () => this.navigateTo('/'), 'Go to Home page');
        this.addShortcut('Alt+L', () => this.navigateTo('/log'), 'Go to Log Contact page');
        this.addShortcut('Alt+C', () => this.navigateTo('/contacts'), 'View All Contacts');
        this.addShortcut('Alt+S', () => this.navigateTo('/stats'), 'View Statistics');
        this.addShortcut('Alt+M', () => this.navigateTo('/map'), 'View Contact Map');
        this.addShortcut('Alt+O', () => this.navigateTo('/objectives'), 'View Objectives');
        this.addShortcut('Alt+T', () => this.navigateTo('/setup'), 'Station Setup');
        
        // Form navigation shortcuts (when in forms)
        this.addShortcut('Tab', null, 'Next field');
        this.addShortcut('Shift+Tab', null, 'Previous field');
        this.addShortcut('Enter', () => this.handleEnterKey(), 'Submit form or next field');
        this.addShortcut('Escape', () => this.handleEscapeKey(), 'Cancel/Clear or close modals');
        
        // Quick field access (on log contact page)
        this.addShortcut('Alt+1', () => this.focusField('callsign'), 'Focus Callsign field');
        this.addShortcut('Alt+2', () => this.focusField('frequency'), 'Focus Frequency field');
        this.addShortcut('Alt+3', () => this.focusField('mode'), 'Focus Mode field');
        this.addShortcut('Alt+4', () => this.focusField('rst_sent'), 'Focus RST Sent field');
        this.addShortcut('Alt+5', () => this.focusField('rst_received'), 'Focus RST Received field');
        this.addShortcut('Alt+6', () => this.focusField('exchange_received'), 'Focus Exchange Received field');
        this.addShortcut('Alt+7', () => this.focusField('notes'), 'Focus Notes field');
        
        // Quick RST shortcuts (when in RST fields)
        this.addShortcut('Ctrl+5', () => this.setRST('599'), 'Set RST to 599');
        this.addShortcut('Ctrl+9', () => this.setRST('59'), 'Set RST to 59');
        
        // Mode selection shortcuts (when in mode field)
        this.addShortcut('Ctrl+P', () => this.setMode('SSB'), 'Set mode to SSB (Phone)');
        this.addShortcut('Ctrl+C', () => this.setMode('CW'), 'Set mode to CW');
        this.addShortcut('Ctrl+D', () => this.setMode('DIGITAL'), 'Set mode to Digital');
        
        // Action shortcuts
        this.addShortcut('Ctrl+Enter', () => this.submitForm(), 'Submit current form');
        this.addShortcut('Ctrl+R', () => this.clearForm(), 'Clear/Reset form');
        this.addShortcut('Alt+N', () => this.newContact(), 'New contact (clear form)');
        
        // Utility shortcuts
        this.addShortcut('F1', () => this.showHelp(), 'Show keyboard shortcuts help');
        this.addShortcut('Alt+?', () => this.showHelp(), 'Show keyboard shortcuts help');
        this.addShortcut('Ctrl+/', () => this.toggleShortcuts(), 'Enable/disable shortcuts');
        
        // Theme shortcuts
        this.addShortcut('Alt+D', () => this.toggleDarkMode(), 'Toggle between light/dark theme');
        this.addShortcut('Ctrl+T', () => this.openThemeSelector(), 'Open theme selector');
    }
    
    addShortcut(keyCombo, handler, description) {
        this.shortcuts.set(keyCombo.toLowerCase(), {
            handler: handler,
            description: description,
            combo: keyCombo
        });
    }
    
    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (!this.isEnabled) return;
            
            // Don't handle shortcuts when typing in input fields (except for special cases)
            if (this.isInputField(e.target) && !this.isSpecialKey(e)) {
                return;
            }
            
            const combo = this.getKeyCombo(e);
            const shortcut = this.shortcuts.get(combo);
            
            if (shortcut && shortcut.handler) {
                e.preventDefault();
                try {
                    shortcut.handler();
                } catch (error) {
                    console.error('Shortcut handler error:', error);
                }
            }
        });
        
        // Handle special Enter key behavior in forms
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && this.isInputField(e.target)) {
                // In log form, move to next field instead of submitting
                if (window.location.pathname === '/log' && !e.ctrlKey) {
                    e.preventDefault();
                    this.moveToNextField(e.target);
                }
            }
        });
    }
    
    getKeyCombo(event) {
        const keys = [];
        
        if (event.ctrlKey) keys.push('Ctrl');
        if (event.altKey) keys.push('Alt');
        if (event.shiftKey) keys.push('Shift');
        
        // Handle special keys
        let key = event.key;
        if (key === ' ') key = 'Space';
        else if (key.length === 1) key = key.toUpperCase();
        
        keys.push(key);
        
        return keys.join('+').toLowerCase();
    }
    
    isInputField(element) {
        const inputTypes = ['INPUT', 'TEXTAREA', 'SELECT'];
        return inputTypes.includes(element.tagName) || element.contentEditable === 'true';
    }
    
    isSpecialKey(event) {
        // These key combos should work even in input fields
        const specialCombos = ['f1', 'alt+?', 'escape', 'ctrl+enter', 'ctrl+/', 'alt+d'];
        const combo = this.getKeyCombo(event);
        return specialCombos.includes(combo);
    }
    
    // Navigation functions
    navigateTo(url) {
        window.location.href = url;
    }
    
    focusField(fieldName) {
        const field = document.getElementById(fieldName) || document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.focus();
            if (field.tagName === 'INPUT' && field.type === 'text') {
                field.select();
            }
        }
    }
    
    setRST(value) {
        const activeElement = document.activeElement;
        if (activeElement && (activeElement.name === 'rst_sent' || activeElement.name === 'rst_received')) {
            activeElement.value = value;
            // Trigger change event
            activeElement.dispatchEvent(new Event('change', { bubbles: true }));
        } else {
            // Set both RST fields if none focused
            const rstSent = document.querySelector('[name="rst_sent"]');
            const rstReceived = document.querySelector('[name="rst_received"]');
            if (rstSent) rstSent.value = value;
            if (rstReceived) rstReceived.value = value;
        }
    }
    
    setMode(mode) {
        const modeField = document.querySelector('[name="mode"]');
        if (modeField) {
            modeField.value = mode;
            modeField.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }
    
    handleEnterKey() {
        const activeElement = document.activeElement;
        if (this.isInputField(activeElement)) {
            this.moveToNextField(activeElement);
        }
    }
    
    handleEscapeKey() {
        // Close modals first
        const modalBackdrop = document.querySelector('.modal.show');
        if (modalBackdrop) {
            const modal = bootstrap.Modal.getInstance(modalBackdrop);
            if (modal) modal.hide();
            return;
        }
        
        // Clear active field
        const activeElement = document.activeElement;
        if (this.isInputField(activeElement)) {
            activeElement.blur();
            if (activeElement.tagName === 'INPUT' || activeElement.tagName === 'TEXTAREA') {
                activeElement.value = '';
            }
        }
    }
    
    moveToNextField(currentField) {
        const form = currentField.closest('form');
        if (!form) return;
        
        const formElements = Array.from(form.elements).filter(el => 
            !el.disabled && el.type !== 'hidden' && el.type !== 'submit'
        );
        
        const currentIndex = formElements.indexOf(currentField);
        const nextIndex = (currentIndex + 1) % formElements.length;
        
        if (formElements[nextIndex]) {
            formElements[nextIndex].focus();
            if (formElements[nextIndex].type === 'text') {
                formElements[nextIndex].select();
            }
        }
    }
    
    submitForm() {
        const form = document.querySelector('form');
        if (form) {
            const submitButton = form.querySelector('[type="submit"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
    
    clearForm() {
        const form = document.querySelector('form');
        if (form && confirm('Clear all form fields?')) {
            form.reset();
            // Focus first field
            const firstField = form.querySelector('input:not([type="hidden"]), textarea, select');
            if (firstField) firstField.focus();
        }
    }
    
    newContact() {
        if (window.location.pathname === '/log') {
            this.clearForm();
        } else {
            this.navigateTo('/log');
        }
    }
    
    toggleDarkMode() {
        // Find current theme and toggle to its counterpart
        const currentTheme = localStorage.getItem('theme') || 'light';
        let newTheme;
        
        if (currentTheme === 'light') {
            newTheme = 'dark';
        } else if (currentTheme === 'dark') {
            newTheme = 'light';
        } else if (currentTheme.includes('-light')) {
            newTheme = currentTheme.replace('-light', '');
        } else {
            // Assume it's a dark variant, try to make it light
            newTheme = currentTheme + '-light';
        }
        
        // Apply theme using existing function
        if (typeof applyTheme === 'function') {
            applyTheme(newTheme);
            localStorage.setItem('theme', newTheme);
        }
    }
    
    openThemeSelector() {
        const themeDropdown = document.getElementById('themeDropdown');
        if (themeDropdown) {
            const dropdown = new bootstrap.Dropdown(themeDropdown);
            dropdown.show();
        }
    }
    
    toggleShortcuts() {
        this.isEnabled = !this.isEnabled;
        const status = this.isEnabled ? 'enabled' : 'disabled';
        this.showToast(`Keyboard shortcuts ${status}`, this.isEnabled ? 'success' : 'warning');
    }
    
    showHelp() {
        if (this.helpModalVisible) return;
        
        this.helpModalVisible = true;
        const modal = this.createHelpModal();
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
            this.helpModalVisible = false;
        });
    }
    
    createHelpModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        
        const shortcuts = Array.from(this.shortcuts.entries())
            .map(([combo, data]) => ({ combo, ...data }))
            .sort((a, b) => a.combo.localeCompare(b.combo));
        
        const categories = {
            'Navigation': shortcuts.filter(s => s.combo.startsWith('Alt+') && s.description.includes('Go to')),
            'Form Fields': shortcuts.filter(s => s.combo.startsWith('Alt+') && s.description.includes('Focus')),
            'Quick Actions': shortcuts.filter(s => s.combo.startsWith('Ctrl+') && !s.description.includes('Set')),
            'Quick Values': shortcuts.filter(s => s.description.includes('Set')),
            'General': shortcuts.filter(s => !['Alt+', 'Ctrl+'].some(prefix => s.combo.startsWith(prefix)) || s.combo === 'F1')
        };
        
        let categorizedShortcuts = '';
        Object.entries(categories).forEach(([category, shortcuts]) => {
            if (shortcuts.length > 0) {
                categorizedShortcuts += `
                    <h6 class="mt-3 mb-2 text-primary">${category}</h6>
                    ${shortcuts.map(s => `
                        <div class="d-flex justify-content-between py-1">
                            <span><kbd>${s.combo}</kbd></span>
                            <span class="ms-3">${s.description}</span>
                        </div>
                    `).join('')}
                `;
            }
        });
        
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="bi bi-keyboard"></i> Keyboard Shortcuts
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="text-muted">Use these keyboard shortcuts for rapid contest logging:</p>
                        ${categorizedShortcuts}
                        <div class="mt-3 p-3 bg-light rounded">
                            <small class="text-muted">
                                <i class="bi bi-info-circle"></i> 
                                <strong>Tip:</strong> Most shortcuts work globally, but form shortcuts work best on the Log Contact page.
                                Use <kbd>Ctrl+/</kbd> to temporarily disable shortcuts if needed.
                            </small>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        `;
        
        return modal;
    }
    
    showToast(message, type = 'info') {
        // Create toast if bootstrap toasts are available
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi bi-keyboard me-2"></i>${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
        
        toast.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast);
        });
    }
    
    addShortcutHints() {
        // Add shortcut hints to form labels
        const fieldMappings = {
            'callsign': 'Alt+1',
            'frequency': 'Alt+2', 
            'mode': 'Alt+3',
            'rst_sent': 'Alt+4',
            'rst_received': 'Alt+5',
            'exchange_received': 'Alt+6',
            'notes': 'Alt+7'
        };
        
        Object.entries(fieldMappings).forEach(([fieldName, shortcut]) => {
            const field = document.getElementById(fieldName) || document.querySelector(`[name="${fieldName}"]`);
            if (field) {
                const label = document.querySelector(`label[for="${fieldName}"]`);
                if (label && !label.querySelector('.shortcut-hint')) {
                    const hint = document.createElement('small');
                    hint.className = 'shortcut-hint text-muted ms-2';
                    hint.innerHTML = `<kbd class="small">${shortcut}</kbd>`;
                    label.appendChild(hint);
                }
            }
        });
    }
}

// Initialize shortcuts when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        window.wfdShortcuts = new WFDKeyboardShortcuts();
    } else {
        console.warn('Bootstrap not found, keyboard shortcuts disabled');
    }
});