"""v2: a rules digest (verbatim lines, with who said them) plus an optional one-sentence gist.

Why: a 1B model gets "who did what" wrong. So the facts come straight from the chat, and the
model only gets to write a short gist that must not name anyone. The checker rejects a gist
that names a person, invents a number, or is not one sentence."""
import re
from .parser import Chat
from .questions import stats
from .brief import valid

TIME = re.compile(r"\b\d{1,2}(:\d{2})?\s?(am|pm)\b|\b\d{1,2}:\d{2}\b|\b(mon|tues|wednes|thurs|fri|satur|sun)day\b|"
                  r"\b(today|tomorrow|tonight|midnight)\b|\b\d{1,2}(st|nd|rd|th)\b|\bbetween \d+ and \d+\b", re.I)
NUM = re.compile(r"\b\d{3,}\b|\b\d{1,2} (confirmed|beds|people)\b", re.I)
DECIDE = re.compile(r"\b(booked|done|confirmed|moved|decided|bring|i'll|will|need|needs|must|max|have to|someone|closes|due)\b", re.I)
ASK = re.compile(r"\?")
# v3: statements about a problem or a cause carry no time or question, so v2 skipped them
PROBLEM = re.compile(r"\b(stuck|broken|down|not working|doesn't work|bug|cause|found the|fix|leak|noise|noisy|out of|missing|lost|cancelled|closed|closes|late|delay|delayed)\b", re.I)

def digest_lines(chat: Chat, you: str = "", cap: int = 10, v3: bool = False):
    scored = []
    for i, m in enumerate(chat.human):
        if m.media:
            continue
        t = m.text
        tags = []
        if TIME.search(t) or NUM.search(t): tags.append("when/how much")
        if ASK.search(t): tags.append("question")
        if DECIDE.search(t): tags.append("plan")
        if v3 and PROBLEM.search(t): tags.append("problem")
        if you and you.lower() in t.lower(): tags.append("you")
        if tags:
            scored.append((len(tags), i, m, tags))
    keep = sorted(sorted(scored, key=lambda x: (-x[0], x[1]))[:cap], key=lambda x: x[1])
    return [(m, tags) for _, _, m, tags in keep]

def gist_prompt(chat: Chat) -> str:
    body = "\n".join(f"{m.text[:120]}" for m in chat.human[:40])
    return ("Here is a group chat with the speaker names removed:\n" + body +
            "\n\nIn ONE short sentence (max 18 words), say what this chat is about. "
            "Do not name any person. Do not add numbers or dates.")

def gist_ok(g: str, chat: Chat) -> bool:
    g = g.strip()
    if not g or len(g.split()) > 24 or "\n" in g: return False
    names = [n.lower() for n in chat.senders]
    low = g.lower()
    if any(re.search(r"\b" + re.escape(p) + r"\b", low) for n in names for p in n.split()): return False
    if re.search(r"\d", g): return False
    return valid(g, chat, max_words=24)

def render(chat: Chat, llm=None, you: str = "", v3: bool = True):
    s = stats(chat)
    lines = digest_lines(chat, you, cap=12 if v3 else 10, v3=v3)
    head = f"{s['messages']} messages, {len(s['senders'])} people, {s['first']} to {s['last']}."
    out = [head]
    src = "rules"
    if llm is not None and lines:
        r = llm.create_chat_completion(messages=[{"role": "user", "content": gist_prompt(chat)}],
                                       max_tokens=48, temperature=0.0)
        g = r["choices"][0]["message"]["content"].strip().strip('"*').split("\n")[0].strip()
        if gist_ok(g, chat):
            out.append("Gist: " + g); src = "gemma"
    if not lines:
        out.append("Nothing needs you.")
    else:
        out.append("Lines worth reading (verbatim):")
        out += [f"- {m.sender}: {m.text[:110]}" for m, _ in lines]
    return "\n".join(out), src
