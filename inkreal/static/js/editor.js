document.addEventListener('DOMContentLoaded', function() {
    var textarea = document.getElementById('contentInput');
    var wordCount = document.getElementById('wordCount');
    var charCount = document.getElementById('charCount');
    var scorePreview = document.getElementById('humanScorePreview');
    var scoreFill = document.getElementById('humanScoreFill');
    var scoreLabel = document.getElementById('humanScoreLabel');

    if (!textarea) return;

    function autoResize() {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    }

    textarea.addEventListener('input', function() {
        autoResize();
        updateCounts();
        debounceHumanCheck();
    });

    autoResize();

    function updateCounts() {
        var text = textarea.value.trim();
        var words = text ? text.split(/\s+/).length : 0;
        var chars = text.length;
        wordCount.textContent = words + ' word' + (words !== 1 ? 's' : '');
        charCount.textContent = chars + ' character' + (chars !== 1 ? 's' : '');
    }

    var humanCheckTimer;

    function debounceHumanCheck() {
        clearTimeout(humanCheckTimer);
        humanCheckTimer = setTimeout(checkHumanScore, 1500);
    }

    function checkHumanScore() {
        var text = textarea.value.trim();
        if (text.length < 100) { scorePreview.style.display = 'none'; return; }
        fetch('/api/human-check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            scorePreview.style.display = 'flex';
            scoreFill.style.width = data.score + '%';
            if (data.score >= 70) { scoreFill.style.background = '#16A34A'; }
            else if (data.score >= 50) { scoreFill.style.background = '#F59E0B'; }
            else { scoreFill.style.background = '#DC2626'; }
            scoreLabel.textContent = '✦ ' + data.label + ' (' + data.score + '%)';
        })
        .catch(function() { scorePreview.style.display = 'none'; });
    }

    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault();
            var start = this.selectionStart;
            var end = this.selectionEnd;
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
    });
});
