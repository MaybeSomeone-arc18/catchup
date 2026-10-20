"""Two-line morning brief with a local open-weight model.
Rules flag the load-bearing lines; the model only writes prose. Every name, number and
date-like token in the output is checked against the source chat; on failure an
extractive template brief is used instead."""
import re
from .parser import Chat
from .questions import flagged, stats

def _tokens(text):
    return set(t.lower() for t in re.findall(r"[A-Za-z][A-Za-z']+|\d+(?:[.:]\d+)?", text))

def _load_bearing(text):
    return set(t.lower() for t in re.findall(r"\b[A-Z][a-z]+\b|\d+(?:[.:]\d+)?|\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", text))

def source_vocab(chat):
    return _tokens(" ".join(m.text + " " + m.sender for m in chat.human))

STOPCAP = set("""the a an i we you they he she it and or but so to in on at for of is are was were be been if then than
that this these those there here what when who how why which can could should will would do does did no not none yes ok
okay morning evening night day today tomorrow tonight yesterday someone everyone anyone one two three also just still
already yet maybe probably about with from into over after before between group chat chats people let nothing something
everything anything mostly mainly waiting pending unanswered answered quiet busy active long short small big new old first
last next early late soon later now again back off up down out very really quite too even only all some any much many few
things stuff plan plans question questions update updates news summary brief line lines talked discussed decided asked
shared sent going coming booked booking got get had has have said says went made make took take gave give done""".split())

def source_exact(chat):
    return set(re.findall(r"[A-Za-z][A-Za-z']+|\d+(?:[.:]\d+)?", " ".join(m.text + " " + m.sender for m in chat.human)))

def valid(brief, chat, max_words=90):
    if not brief.strip() or len(brief.split()) > max_words:
        return False
    vocab = source_vocab(chat); exact = source_exact(chat)
    for tok in _load_bearing(brief):
        if re.fullmatch(r"\d+", tok) and int(tok) <= 31: continue
        if tok in exact or tok in vocab: continue
        if tok in STOPCAP: continue
        return False
    return True

def prompt(chat, you=""):
    s = stats(chat); key = [chat.human[i] for i in flagged(chat, you)][:12]
    key_block = "\n".join(f"- {m.sender}: {m.text[:140]}" for m in key) or "(none)"
    return ("You write morning briefings for a lazy reader who skipped a group chat.\n"
        + (f"The reader is {you}.\n" if you else "")
        + f"The chat had {s['messages']} messages from {len(s['senders'])} people ({', '.join(s['senders'])}), between {s['first']} and {s['last']}.\n"
        "Key lines a rules pass already picked out:\n" + key_block + "\n"
        "Write a brief of at most 3 short lines:\nline 1: what the chat was mostly about\n"
        "line 2: anything decided, with the exact day/time if one was set\n"
        "line 3: questions still waiting for an answer, or 'nothing waiting'\n"
        "Use only names, numbers and dates that appear above. Plain words. No greeting.")

def template(chat, you=""):
    s = stats(chat); key = [chat.human[i] for i in flagged(chat, you)][:6]
    lines = [f"{s['messages']} messages from {len(s['senders'])} people ({', '.join(s['senders'])}) between {s['first']} and {s['last']}."]
    lines.append("Worth a look: " + " | ".join(f"{m.sender}: {m.text[:80]}" for m in key) if key else "Nothing urgent was flagged.")
    return "\n".join(lines)

def make(chat, you="", llm=None):
    if llm is not None:
        r = llm.create_chat_completion(messages=[{"role": "user", "content": prompt(chat, you)}], max_tokens=180, temperature=0.2)
        t = r["choices"][0]["message"]["content"].strip().strip('"*')
        if valid(t, chat): return t, "gemma"
    return template(chat, you), "template"
