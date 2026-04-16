(function () {
    function findFieldRow(element) {
        return (
            element.closest('.form-row') ||
            element.closest('.fieldBox') ||
            element.closest('.field-' + (element.name || '')) ||
            null
        );
    }

    function toggleRow(row, isVisible) {
        if (!row) {
            return;
        }
        row.style.display = isVisible ? '' : 'none';
    }

    function initBlockEditor() {
        var typeInput = document.getElementById('id_type');
        if (!typeInput) {
            return;
        }

        var editorFields = Array.prototype.slice.call(
            document.querySelectorAll('[data-block-editor-type]')
        );
        var fallbackField = document.querySelector('[data-block-editor-fallback]');
        var guide = document.querySelector('[data-block-editor-guide]');
        var guideTitle = document.querySelector('[data-block-editor-guide-title]');
        var guideText = document.querySelector('[data-block-editor-guide-text]');
        var supportedTypes = {};

        editorFields.forEach(function (field) {
            supportedTypes[field.getAttribute('data-block-editor-type')] = true;
        });

        function updateGuide(blockType, isSupported) {
            if (!guide || !guideTitle || !guideText) {
                return;
            }

            var emptyTitle = guide.getAttribute('data-empty-title') || '';
            var emptyText = guide.getAttribute('data-empty-text') || '';
            var fallbackTitle = guide.getAttribute('data-fallback-title') || '';
            var fallbackText = guide.getAttribute('data-fallback-text') || '';

            if (!blockType) {
                guideTitle.textContent = emptyTitle;
                guideText.textContent = emptyText;
                return;
            }

            if (!isSupported) {
                guideTitle.textContent = fallbackTitle;
                guideText.textContent = fallbackText;
                return;
            }

            guideTitle.textContent = 'Человеческий редактор для типа «' + blockType + '»';
            guideText.textContent = 'Показываются только поля, относящиеся к выбранному типу. JSON будет собран автоматически при сохранении.';
        }

        function sync() {
            var blockType = (typeInput.value || '').trim().toLowerCase();
            var isSupported = !!supportedTypes[blockType];

            editorFields.forEach(function (field) {
                var row = findFieldRow(field);
                var fieldType = field.getAttribute('data-block-editor-type');
                toggleRow(row, isSupported && fieldType === blockType);
            });

            if (fallbackField) {
                toggleRow(findFieldRow(fallbackField), !!blockType && !isSupported);
            }

            updateGuide(blockType, isSupported);
        }

        typeInput.addEventListener('input', sync);
        typeInput.addEventListener('change', sync);
        sync();
    }

    document.addEventListener('DOMContentLoaded', initBlockEditor);
})();
