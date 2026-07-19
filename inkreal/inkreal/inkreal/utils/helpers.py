from datetime import datetime, timezone
import math
import re
import markdown2
import bleach


def _parse_dt(t):
    if t is None:
        return None
    if isinstance(t, str):
        try:
            dt = datetime.fromisoformat(t.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except Exception:
            return None
    if isinstance(t, (int, float)):
        return datetime.fromtimestamp(t / 1000, tz=timezone.utc)
    if hasattr(t, "tzinfo"):
        if t.tzinfo is None:
            return t.replace(tzinfo=timezone.utc)
        return t
    return None


def time_ago(t):
    dt = _parse_dt(t)
    if dt is None:
        return "just now"
    diff = (datetime.now(timezone.utc) - dt).total_seconds()
    if diff < 60:
        return "just now"
    if diff < 3600:
        return f"{int(diff/60)}m ago"
    if diff < 86400:
        return f"{int(diff/3600)}h ago"
    if diff < 604800:
        return f"{int(diff/86400)}d ago"
    if diff < 2592000:
        return f"{int(diff/604800)}w ago"
    if diff < 31536000:
        return f"{int(diff/2592000)}mo ago"
    return f"{int(diff/31536000)}y ago"


def duration_since(t):
    dt = _parse_dt(t)
    if dt is None:
        return "0m"
    diff = (datetime.now(timezone.utc) - dt).total_seconds()
    if diff < 3600:
        return f"{max(1,int(diff/60))}m"
    if diff < 86400:
        return f"{int(diff/3600)}h"
    if diff < 604800:
        return f"{int(diff/86400)}d"
    return f"{int(diff/604800)}w"


def reading_time(content):
    if not content:
        return "1 min read"
    words = len(content.split())
    return f"{max(1, math.ceil(words/200))} min read"


def render_markdown(text):
    if not text:
        return ""
    html = markdown2.markdown(text, extras=["fenced-code-blocks", "tables", "break-on-newline", "header-ids", "strike"])
    tags = ["p","br","strong","em","u","h1","h2","h3","h4","h5","h6","ul","ol","li","blockquote","code","pre","a","img","table","thead","tbody","tr","th","td","hr","del","sup","sub"]
    attrs = {"a":["href","title","target","rel"],"img":["src","alt","title"],"code":["class"],"pre":["class"],"*":["id","class"]}
    return bleach.clean(html, tags=tags, attributes=attrs)


def truncate_text(text, length=200):
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(" ", 1)[0] + "..."


def generate_slug(title):
    import uuid
    slug = re.sub(r"[^\w\s-]", "", (title or "post").lower().strip())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")[:60]
    return f"{slug}-{uuid.uuid4().hex[:8]}"


def extract_tags(text):
    if not text:
        return []
    tags = re.findall(r"#([a-zA-Z0-9_]{2,30})", text)
    seen = set()
    result = []
    for t in tags:
        low = t.lower()
        if low not in seen:
            seen.add(low)
            result.append(low)
    return result[:8]


def get_cover_image(topic="general"):
    covers = {
        "technology": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&q=80",
        "writing": "https://images.unsplash.com/photo-1455390582262-044cdead277a?w=1200&q=80",
        "life": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&q=80",
        "career": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80",
        "startups": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80",
        "design": "https://images.unsplash.com/photo-1561070791-2526d30994b8?w=1200&q=80",
        "buildinpublic": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=1200&q=80",
        "general": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=1200&q=80"
    }
    return covers.get(topic, covers["general"])
