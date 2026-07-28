document.addEventListener('DOMContentLoaded', function() {
    var streakNumbers = document.querySelectorAll('.streak-number, .streak-stat-number');
    streakNumbers.forEach(function(el) {
        var target = parseInt(el.textContent) || 0;
        if (target === 0) return;
        var current = 0;
        var duration = 800;
        var step = target / (duration / 16);
        el.textContent = '0';
        var timer = setInterval(function() {
            current += step;
            if (current >= target) { el.textContent = target; clearInterval(timer); }
            else { el.textContent = Math.floor(current); }
        }, 16);
    });
    var streakBars = document.querySelectorAll('.streak-bar-fill');
    streakBars.forEach(function(bar) {
        var width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() { bar.style.width = width; }, 200);
    });
});
