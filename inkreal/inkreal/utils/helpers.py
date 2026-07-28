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
        return f"{int(seconds / 60)}m ago"
    elif seconds < 86400:
        return f"{int(seconds / 3600)}h ago"
    elif seconds < 604800:
        return f"{int(seconds / 86400)}d ago"
    elif seconds < 2592000:
        return f"{int(seconds / 604800)}w ago"
    elif seconds < 31536000:
        return f"{int(seconds / 2592000)}mo ago"
    else:
        return f"{int(seconds / 31536000)}y ago"


def reading_time(content):
    if not content:
        return "1 min read"
    words = len(content.split())
    minutes = max(1, math.ceil(words / 200))
    return f"{minutes} min read"


def render_markdown(text):
    if not text:
        return ""
    html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "break-on-newline", "header-ids"])
    allowed_tags = ["p", "br", "strong", "em", "u", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote", "code", "pre", "a", "img", "table", "thead", "tbody", "tr", "th", "td", "hr", "del", "sup", "sub"]
    allowed_attrs = {"a": ["href", "title", "target"], "img": ["src", "alt", "title"], "code": ["class"], "pre": ["class"], "*": ["id", "class"]}
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)


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
    return f"{slug}-{uuid.uuid4().hex[:8]}"


def get_cover_image(topic="general", seed=None):
    covers = {
        "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
        "writing": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&q=80",
        "life": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80",
        "career": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80",
        "philosophy": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=1200&q=80",
        "creativity": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=1200&q=80",
        "health": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80",
        "books": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1200&q=80",
        "startups": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80",
        "design": "https://images.unsplash.com/photo-1561070791-2526d30994b8?w=1200&q=80",
        "general": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=80"
    }
    return covers.get(topic, covers["general"])
