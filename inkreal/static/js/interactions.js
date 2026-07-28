function submitComment(postId) {
    var input = document.getElementById('commentInput');
    var content = input.value.trim();
    if (!content) { input.style.borderColor = '#DC2626'; setTimeout(function() { input.style.borderColor = ''; }, 2000); return; }
    fetch('/api/comment/' + postId, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.error) { if (data.error === 'Login required') { window.location.href = '/auth/login'; } return; }
        var commentsList = document.getElementById('commentsList');
        var noComments = commentsList.querySelector('.no-comments');
        if (noComments) noComments.remove();
        commentsList.insertAdjacentHTML('beforeend', createCommentHTML(data.comment));
        input.value = '';
        var countEl = document.querySelector('.comments-count');
        if (countEl) {
            var currentCount = parseInt(countEl.textContent.replace(/\D/g, '')) || 0;
            countEl.textContent = '(' + (currentCount + 1) + ')';
        }
        showToast('Comment posted!');
    })
    .catch(function(err) { console.error('Comment error:', err); });
}

function createCommentHTML(comment) {
    return '<div class="comment" id="comment-' + comment.id + '">' +
        '<div class="comment-header">' +
            '<a href="/profile/' + comment.author_handle + '" class="comment-author">' +
                '<div class="comment-avatar" style="background-color:' + (comment.author_avatar_color || '#4111CC') + '">' + (comment.author_avatar_letter || '?') + '</div>' +
                '<div class="comment-author-info">' +
                    '<span class="comment-author-name">' + comment.author_name + '</span>' +
                    '<span class="comment-time">just now</span>' +
                '</div>' +
            '</a>' +
        '</div>' +
        '<div class="comment-body">' + escapeHtml(comment.content) + '</div>' +
    '</div>';
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
