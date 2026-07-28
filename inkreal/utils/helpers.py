from datetime import datetime, timezone
import math
import markdown2
import bleach


def time_ago(timestamp):
    if timestamp is None:
        return "just now"

    if isinstance(timestamp, str):
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return "some time ago"
    elif isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    else:
        dt = timestamp

    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        m = int(seconds / 60)
        return f"{m}m ago"
    elif seconds < 86400:
        h = int(seconds / 3600)
        return f"{h}h ago"
    elif seconds < 604800:
        d = int(seconds / 86400)
        return f"{d}d ago"
    elif seconds < 2592000:
        w = int(seconds / 604800)
        return f"{w}w ago"
    elif seconds < 31536000:
        mo = int(seconds / 2592000)
        return f"{mo}mo ago"
    else:
        y = int(seconds / 31536000)
        return f"{y}y ago"


def reading_time(content):
    if not content:
        return "1 min read"
    words = len(content.split())
    minutes = max(1, math.ceil(words / 200))
    return f"{minutes} min read"


def render_markdown(text):
    if not text:
        return ""
    html = markdown2.markdown(
        text,
        extras=["fenced-code-blocks", "tables", "break-on-newline", "header-ids"]
    )
    allowed_tags = [
        "p", "br", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "blockquote", "code", "pre", "a", "img",
        "table", "thead", "tbody", "tr", "th", "td", "hr", "del", "sup", "sub"
    ]
    allowed_attrs = {
        "a": ["href", "title", "target"],
        "img": ["src", "alt", "title"],
        "code": ["class"],
        "pre": ["class"],
        "*": ["id", "class"]
    }
    clean = bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)
    return clean


def truncate_text(text, length=160):
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def generate_slug(title):
    import re
    import uuid
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    slug = slug.strip("-")
    short_id = uuid.uuid4().hex[:8]
    return f"{slug}-{short_id}"
