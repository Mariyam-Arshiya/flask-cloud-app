import re


def analyze_human_score(text):
    if not text or len(text.strip()) < 20:
        return {"score": 50, "indicators": [], "label": "Too short to analyze"}
    score = 70
    indicators = []
    ai_phrases = ["in today's world", "it's important to note", "in conclusion", "furthermore", "moreover", "it is worth mentioning", "in the realm of", "navigating the", "landscape of", "let's dive in", "without further ado", "game-changer", "at the end of the day", "leverage", "synergy", "revolutionize", "cutting-edge", "groundbreaking", "seamlessly", "robust", "comprehensive guide", "unlock the power", "deep dive", "paradigm shift", "holistic approach", "in this article we will", "as we all know", "it goes without saying"]
    text_lower = text.lower()
    ai_phrase_count = sum(1 for phrase in ai_phrases if phrase in text_lower)
    if ai_phrase_count >= 4:
        score -= 25
        indicators.append("Uses many common AI phrases")
    elif ai_phrase_count >= 2:
        score -= 10
        indicators.append("Some generic phrasing detected")
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) >= 3:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance > 30:
            score += 8
            indicators.append("Good sentence variety")
        elif variance < 5:
            score -= 10
            indicators.append("Very uniform sentence structure")
    personal_words = len(re.findall(r"\b(I|my|me|we|our|you|your)\b", text))
    word_count = len(text.split())
    personal_ratio = personal_words / max(word_count, 1)
    if personal_ratio > 0.03:
        score += 10
        indicators.append("Personal voice detected")
    contractions = len(re.findall(r"\b(don't|can't|won't|I'm|I've|it's|that's|there's|isn't|aren't|wasn't|weren't|couldn't|wouldn't|shouldn't|didn't|hasn't|haven't)\b", text, re.IGNORECASE))
    if contractions >= 2:
        score += 5
        indicators.append("Natural contractions used")
    bullet_count = text.count("- ") + text.count("* ")
    if bullet_count > 8:
        score -= 8
        indicators.append("Heavy list formatting")
    score = max(10, min(100, score))
    if score >= 80:
        label = "Feels authentically human"
    elif score >= 60:
        label = "Mostly human feel"
    elif score >= 40:
        label = "Mixed signals"
    else:
        label = "Might be AI-assisted"
    return {"score": score, "indicators": indicators, "label": label}
