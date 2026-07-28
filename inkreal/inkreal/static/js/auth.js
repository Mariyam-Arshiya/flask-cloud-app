document.addEventListener('DOMContentLoaded', function() {
    var handleInput = document.getElementById('handle');
    if (handleInput) {
        handleInput.addEventListener('input', function() {
            this.value = this.value.toLowerCase().replace(/[^a-z0-9_]/g, '');
        });
    }
});
