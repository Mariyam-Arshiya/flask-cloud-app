document.addEventListener('DOMContentLoaded', function() {
    initFlashMessages();
});

function initFlashMessages() {
    document.querySelectorAll('.flash-message').forEach(function(f) {
        setTimeout(function() {
            f.style.opacity = '0';
            f.style.transform = 'translateX(20px)';
            setTimeout(function() { f.remove(); }, 300);
        }, 4500);
    });
}

function handleLike(btn, postId) {
    fetch('/api/like/' + postId, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) { window.location.href = '/auth/login'; return; }
        var el = btn.querySelector('.like-count');
        if (el) el.textContent = d.count;
        if (d.status === 'added') btn.classList.add('active');
        else btn.classList.remove('active');
    });
}

function handleBookmark(btn, postId) {
    fetch('/api/bookmark/' + postId, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) { window.location.href = '/auth/login'; return; }
        if (d.status === 'added') btn.classList.add('active');
        else btn.classList.remove('active');
    });
}

function handleFollow(btn, userId) {
    fetch('/api/follow/' + userId, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) { if (d.error === 'Login required') window.location.href = '/auth/login'; return; }
        if (d.status === 'followed') { btn.textContent = 'Following'; btn.classList.add('following'); }
        else { btn.textContent = 'Follow'; btn.classList.remove('following'); }
    });
}

function sharePost(title) {
    if (navigator.share) navigator.share({ title: title + ' — InkReal', url: window.location.href });
    else navigator.clipboard.writeText(window.location.href).then(function() { showToast('Link copied'); });
}

function reportPost(postId) {
    var reason = prompt('Why are you reporting this post? (optional)');
    if (reason === null) return;
    fetch('/api/report/' + postId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: reason || 'unspecified' })
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.status === 'reported') showToast('Reported. Thank you.');
    });
}

function showToast(message) {
    var t = document.createElement('div');
    t.className = 'flash-message flash-success';
    t.innerHTML = '<span class="flash-dot"></span> ' + message;
    t.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);z-index:9999;';
    document.body.appendChild(t);
    setTimeout(function() { t.style.opacity = '0'; setTimeout(function() { t.remove(); }, 300); }, 2500);
}
