"""Parse a WhatsApp exported chat (.txt) into messages. Pure rules, no model."""
import re
from dataclasses import dataclass, field

STAMP = re.compile(
    r"^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s+(?P<time>\d{1,2}:\d{2}(?:\s?[AP]M)?)\s+-\s+(?P<rest>.*)$",
    re.IGNORECASE)
SYSTEM_HINTS = ("messages and calls are end-to-end encrypted", "created group", "changed the subject",
    "changed this group's icon", "joined using this group's invite link", "left", "removed", "added",
    "you deleted this message", "this message was deleted", "missed voice call", "missed video call")
MEDIA_TOKENS = ("<media omitted>", "image omitted", "video omitted", "sticker omitted",
                "audio omitted", "document omitted", "gif omitted")

@dataclass
class Message:
    date: str
    time: str
    sender: str
    text: str
    media: bool = False

@dataclass
class Chat:
    messages: list = field(default_factory=list)
    @property
    def human(self):
        return [m for m in self.messages if m.sender]
    @property
    def senders(self):
        seen = []
        for m in self.human:
            if m.sender not in seen:
                seen.append(m.sender)
        return seen

STRONG_SYSTEM = ("end-to-end encrypted", "created group", "changed the subject")

def is_system(text):
    t = text.lower()
    return any(h in t for h in SYSTEM_HINTS)

def parse(text):
    chat = Chat()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = STAMP.match(line)
        if m:
            rest = m.group("rest")
            if ": " in rest:
                sender, body = rest.split(": ", 1)
            else:
                sender, body = "", rest
            # only a line with no "name: " can be a system line; a chat message saying "i left them" is not
            if (not sender and is_system(body)) or any(h in rest.lower() for h in STRONG_SYSTEM):
                continue
            media = any(tok in body.lower() for tok in MEDIA_TOKENS)
            chat.messages.append(Message(m.group("date"), m.group("time"), sender.strip(), body.strip(), media))
        elif chat.messages:
            chat.messages[-1].text += " " + line
    return chat
