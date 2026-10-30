/**
 * YatraSetu: Vanilla JavaScript Interactions
 * Handles delete confirmation modals with accessible keyboard/focus management,
 * client-side validation, flash alerts, and stop ordering.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Flash alert auto-dismiss & close button
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    alertCloseButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            const alert = this.closest('.alert');
            if (alert) {
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 200);
            }
        });
    });

    // 2. Generic Confirmation Modal for Deletion with Accessible Focus & Escape Handling
    const deleteModal = document.getElementById('deleteConfirmModal');
    const deleteForm = document.getElementById('deleteConfirmForm');
    const deleteItemNameSpan = document.getElementById('deleteItemName');
    const deleteCancelBtn = document.getElementById('deleteCancelBtn');
    const deleteWarningText = document.getElementById('deleteWarningText');
    const modalTitle = document.getElementById('modalTitle');
    let lastActiveTrigger = null;

    function closeModal() {
        if (!deleteModal) return;
        deleteModal.classList.remove('active');
        if (lastActiveTrigger && typeof lastActiveTrigger.focus === 'function') {
            lastActiveTrigger.focus();
        }
    }

    if (deleteModal) {
        // Open modal on clicking any trigger with .btn-delete-trigger
        const deleteTriggers = document.querySelectorAll('.btn-delete-trigger');
        deleteTriggers.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                lastActiveTrigger = this;

                const actionUrl = this.getAttribute('data-action');
                const itemName = this.getAttribute('data-name') || 'this item';
                const warningMsg = this.getAttribute('data-warning') || 'This action cannot be undone.';
                const customTitle = this.getAttribute('data-title') || 'Confirm Deletion';

                if (deleteForm) deleteForm.setAttribute('action', actionUrl);
                if (deleteItemNameSpan) deleteItemNameSpan.textContent = itemName;
                if (deleteWarningText) deleteWarningText.textContent = warningMsg;
                if (modalTitle) modalTitle.textContent = customTitle;

                deleteModal.classList.add('active');

                // Shift focus into dialog for accessibility
                if (deleteCancelBtn) {
                    deleteCancelBtn.focus();
                }
            });
        });

        // Close modal on Cancel
        if (deleteCancelBtn) {
            deleteCancelBtn.addEventListener('click', function () {
                closeModal();
            });
        }

        // Close on clicking outside modal-box (backdrop)
        deleteModal.addEventListener('click', function (e) {
            if (e.target === deleteModal) {
                closeModal();
            }
        });

        // Close on Escape key
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && deleteModal.classList.contains('active')) {
                closeModal();
            }
        });
    }

    // 3. Edit Stop Modal with Accessible Focus & Escape Handling
    const editStopModal = document.getElementById('editStopModal');
    const editStopForm = document.getElementById('editStopForm');
    const editStopPlaceName = document.getElementById('editStopPlaceName');
    const modalPlannedDays = document.getElementById('modal_planned_days');
    const modalStopNotes = document.getElementById('modal_stop_notes');
    const editStopCancelBtn = document.getElementById('editStopCancelBtn');
    let lastEditTrigger = null;

    function closeEditModal() {
        if (!editStopModal) return;
        editStopModal.classList.remove('active');
        if (lastEditTrigger && typeof lastEditTrigger.focus === 'function') {
            lastEditTrigger.focus();
        }
    }

    if (editStopModal) {
        const editTriggers = document.querySelectorAll('.btn-edit-stop');
        editTriggers.forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.preventDefault();
                lastEditTrigger = this;

                const actionUrl = this.getAttribute('data-action');
                const placeName = this.getAttribute('data-name') || 'Destination';
                const order = this.getAttribute('data-order') || '';
                const days = this.getAttribute('data-days') || '1';
                const notes = this.getAttribute('data-notes') || '';

                if (editStopForm) editStopForm.setAttribute('action', actionUrl);
                if (editStopPlaceName) editStopPlaceName.textContent = `#${order}: ${placeName}`;
                if (modalPlannedDays) modalPlannedDays.value = days;
                if (modalStopNotes) modalStopNotes.value = notes;

                editStopModal.classList.add('active');
                if (modalPlannedDays) {
                    modalPlannedDays.focus();
                    modalPlannedDays.select();
                }
            });
        });

        if (editStopCancelBtn) {
            editStopCancelBtn.addEventListener('click', function () {
                closeEditModal();
            });
        }

        editStopModal.addEventListener('click', function (e) {
            if (e.target === editStopModal) {
                closeEditModal();
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape' && editStopModal.classList.contains('active')) {
                closeEditModal();
            }
        });
    }

    // 4. "Add First Stop" Smooth Navigation and Focus Handler
    const addFirstStopBtn = document.getElementById('addFirstStopBtn');
    if (addFirstStopBtn) {
        addFirstStopBtn.addEventListener('click', function (e) {
            e.preventDefault();
            const targetSection = document.getElementById('addStopSection');
            const destSelect = document.getElementById('destination_id');

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                targetSection.classList.add('highlight-section');
                setTimeout(() => targetSection.classList.remove('highlight-section'), 2000);
            }

            if (destSelect) {
                setTimeout(() => {
                    destSelect.focus({ preventScroll: true });
                }, 350);
            }
        });
    }

    // 5. Client-side form validation helper
    const validatedForms = document.querySelectorAll('.needs-validation');
    validatedForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            let isValid = true;
            const requiredInputs = form.querySelectorAll('[required]');

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            // Specific check for positive duration numbers
            const durationInputs = form.querySelectorAll('input[type="number"][name*="days"]');
            durationInputs.forEach(input => {
                if (parseInt(input.value, 10) <= 0) {
                    isValid = false;
                    input.classList.add('is-invalid');
                }
            });

            if (!isValid) {
                e.preventDefault();
                alert('Please fill out all required fields with valid values before submitting.');
            }
        });
    });

    // 4. Quick filter reset helper
    const clearFilterBtn = document.getElementById('clearFiltersBtn');
    if (clearFilterBtn) {
        clearFilterBtn.addEventListener('click', function () {
            const form = this.closest('form');
            if (form) {
                form.querySelectorAll('input[type="text"]').forEach(i => i.value = '');
                form.querySelectorAll('select').forEach(s => s.selectedIndex = 0);
                form.submit();
            }
        });
    }
});
