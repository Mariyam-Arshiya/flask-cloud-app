document.addEventListener('DOMContentLoaded', function() {
    var handleInput = document.getElementById('handle');
    if (handleInput) {
        handleInput.addEventListener('input', function() {
            this.value = this.value.toLowerCase().replace(/[^a-z0-9_]/g, '');
        });
    }
    var passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            var val = this.value;
            if (val.length >= 6) { this.style.borderColor = '#16A34A'; }
            else if (val.length >= 3) { this.style.borderColor = '#F59E0B'; }
            else { this.style.borderColor = ''; }
        });
    }
});
