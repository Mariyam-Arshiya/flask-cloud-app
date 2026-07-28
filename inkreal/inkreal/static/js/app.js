document.addEventListener('DOMContentLoaded', function() {
    initFlashMessages();
});

function initFlashMessages() {
    var flashes = document.querySelectorAll('.flash-message');
    flashes.forEach(function(flash) {
        setTimeout(function() {
            flash.style.opacity = '0';
            flash.style.transform = 'translateX(20px)';
            setTimeout(function() { flash.remove(); }, 300);
        }, 4500);
    });
}

function handleUpvote(btn, postId) {
    fetch('/api/upvote/' + postId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.error) { window.location.href = '/auth/login'; return; }
        var countEl = btn.querySelector('.upvote-count');
        if (countEl) countEl.textContent = data.count;
        if (data.status === 'added') { btn.classList.add('active'); }
        else { btn.classList.remove('active'); }
    })
    .catch(function(err) { console.error('Upvote error:', err); });
}

function handleBookmark(btn, postId) {
    fetch('/api/bookmark/' + postId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.error) { window.location.href = '/auth/login'; return; }
        if (data.status === 'added') { btn.classList.add('active'); }
        else { btn.classList.remove('active'); }
    })
    .catch(function(err) { console.error('Bookmark error:', err); });
}

function handleFollow(btn, userId) {
    fetch('/api/follow/' + userId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.error) { if (data.error === 'Login required') { window.location.href = '/auth/login'; } return; }
        if (data.status === 'followed') { btn.textContent = 'Following'; btn.classList.add('following'); }
        else { btn.textContent = 'Follow'; btn.classList.remove('following'); }
    })
    .catch(function(err) { console.error('Follow error:', err); });
}

function sharePost(title) {
    if (navigator.share) {
        navigator.share({ title: title + ' — InkReal', url: window.location.href });
    } else {
        navigator.clipboard.writeText(window.location.href).then(function() { showToast('Link copied to clipboard'); });
    }
}

function showToast(message) {
    var toast = document.createElement('div');
    toast.className = 'flash-message flash-success';
    toast.innerHTML = '<span class="flash-dot"></span> ' + message;
    toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:9999;';
    document.body.appendChild(toast);
    setTimeout(function() {
        toast.style.opacity = '0';
        setTimeout(function() { toast.remove(); }, 300);
    }, 2500);
}
