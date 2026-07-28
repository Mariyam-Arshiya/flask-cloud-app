document.addEventListener('DOMContentLoaded', function() {
    var textarea = document.getElementById('contentInput');
    var wordCount = document.getElementById('wordCount');
    var charCount = document.getElementById('charCount');
    var scorePreview = document.getElementById('humanScorePreview');
    var scoreFill = document.getElementById('humanScoreFill');
    var scoreLabel = document.getElementById('humanScoreLabel');
    var topicSelect = document.getElementById('topicSelect');
    var coverImage = document.getElementById('coverImage');
    var coverUrlInput = document.getElementById('coverUrlInput');

    var covers = {
        technology: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80',
        writing: 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&q=80',
        life: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80',
        career: 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80',
        philosophy: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200&q=80',
        creativity: 'https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=1200&q=80',
        health: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80',
        books: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=80',
        startups: 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80',
        design: 'https://images.unsplash.com/photo-1561070791-2526d30994b8?w=1200&q=80',
        general: 'https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=80'
    };

    if (topicSelect && coverImage) {
        coverUrlInput.value = covers.general;
        topicSelect.addEventListener('change', function() {
            var url = covers[this.value] || covers.general;
            coverImage.src = url;
            coverUrlInput.value = url;
        });
    }

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
            if (data.score >= 70) { scoreFill.style.background = '#166534'; }
            else if (data.score >= 50) { scoreFill.style.background = '#B45309'; }
            else { scoreFill.style.background = '#B91C1C'; }
            scoreLabel.textContent = data.label + ' (' + data.score + '%)';
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
