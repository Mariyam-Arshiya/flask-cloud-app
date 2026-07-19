function submitComment(postId) {
    var input = document.getElementById('commentInput');
    var content = input.value.trim();
    if (!content) { input.style.borderColor = '#B91C1C'; setTimeout(function() { input.style.borderColor = ''; }, 2000); return; }
    fetch('/api/comment/' + postId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.error) { if (d.error === 'Login required') window.location.href = '/auth/login'; return; }
        var list = document.getElementById('commentsList');
        var none = list.querySelector('.no-comments');
        if (none) none.remove();
        list.insertAdjacentHTML('beforeend', createCommentHTML(d.comment));
        input.value = '';
        var c = document.querySelector('.comments-count');
        if (c) { var n = parseInt(c.textContent.replace(/\D/g, '')) || 0; c.textContent = '(' + (n + 1) + ')'; }
        showToast('Comment posted');
    });
}

function createCommentHTML(c) {
    var avatar = c.author_avatar_url
        ? '<img src="' + c.author_avatar_url + '" class="comment-avatar-img" alt="">'
        : '<div class="comment-avatar">' + (c.author_avatar_letter || '?') + '</div>';
    return '<div class="comment" id="comment-' + c.id + '"><div class="comment-header"><a href="/profile/' + c.author_handle + '" class="comment-author">' + avatar + '<div class="comment-author-info"><span class="comment-author-name">' + c.author_name + '</span><span class="comment-time">just now</span></div></a></div><div class="comment-body">' + escapeHtml(c.content) + '</div></div>';
}

function escapeHtml(t) { var d = document.createElement('div'); d.textContent = t; return d.innerHTML; }
