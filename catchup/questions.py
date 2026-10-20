"""Find the messages a lazy reader most needs. Pure rules; the model only writes prose."""
import re
from .parser import Chat
QWORD = re.compile(r"\b(who|what|when|where|why|how|which|can|could|should|shall|are|is|do|does|did|will|would|kya|kab|kahan|kaun)\b", re.I)
DATEISH = re.compile(r"\b(today|tomorrow|tonight|monday|tuesday|wednesday|thursday|friday|saturday|sunday|weekend|am|pm|\d{1,2}[:/]\d{2})\b", re.I)
PLAN = re.compile(r"\b(plan|meet|call|movie|dinner|lunch|trip|exam|deadline|submit|book|ticket|reach|leave|come|bring)\b", re.I)

def flagged(chat, you=""):
    out = []
    for i, m in enumerate(chat.human):
        t = m.text; score = 0
        if "?" in t or QWORD.search(t): score += 2
        if DATEISH.search(t): score += 1
        if PLAN.search(t): score += 1
        if you and you.lower() in t.lower(): score += 2
        if m.media: score -= 1
        if score >= 2: out.append(i)
    return out

def stats(chat):
    h = chat.human; per = {}
    for m in h: per[m.sender] = per.get(m.sender, 0) + 1
    return {"messages": len(h), "media": sum(1 for m in h if m.media), "senders": chat.senders,
            "per_sender": per, "first": f"{h[0].date}, {h[0].time}" if h else "",
            "last": f"{h[-1].date}, {h[-1].time}" if h else ""}
