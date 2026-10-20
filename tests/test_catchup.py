from catchup.parser import parse
from catchup.questions import flagged, stats
from catchup.brief import valid, template, make
GOA = """10/19/26, 9:03 PM - Riya: ok so are we finalising the goa plan tonight or what
10/19/26, 9:07 PM - Dev: train, cheaper. 12619 leaves 21:35
10/19/26, 9:08 PM - Aisha: <Media omitted>
10/19/26, 9:41 PM - Dev: who has the train tickets? did anyone book?
10/19/26, 9:44 PM - Riya: not yet. booking them tomorrow after manav confirms"""
class Fake:
    def __init__(s, t): s.t = t
    def create_chat_completion(s, **k): return {"choices": [{"message": {"content": s.t}}]}
def test_parse_basic():
    c = parse(GOA); assert len(c.human) == 5 and c.senders == ["Riya", "Dev", "Aisha"]
def test_system_lines_dropped():
    assert len(parse("10/19/26, 9:02 PM - Riya: Messages and calls are end-to-end encrypted. x\n10/19/26, 9:03 PM - Riya: hi").human) == 1
def test_continuation_joins():
    c = parse("10/19/26, 9:03 PM - Riya: first\nsecond\n10/19/26, 9:04 PM - Dev: next")
    assert c.messages[0].text == "first second" and len(c.messages) == 2
def test_media_flagged(): assert parse(GOA).human[2].media
def test_flagged_questions():
    c = parse(GOA); p = [c.human[i].text for i in flagged(c)]
    assert any("tickets" in t for t in p) and any("finalising" in t for t in p)
def test_flagged_you():
    assert flagged(parse("10/19/26, 9:03 PM - Riya: sam are you coming friday?\n10/19/26, 9:04 PM - Dev: ok"), you="sam") == [0]
def test_stats():
    s = stats(parse(GOA)); assert s["messages"] == 5 and s["media"] == 1 and s["per_sender"]["Riya"] == 2
def test_valid_ok(): assert valid("Chat was about the goa plan.\nRiya said tickets are booked after manav confirms.\nNothing waiting.", parse(GOA))
def test_reject_name(): assert not valid("Prudhvi booked the tickets.", parse(GOA))
def test_reject_big_number(): assert not valid("2400 messages and 9 people.", parse(GOA))
def test_reject_empty(): assert not valid("  ", parse(GOA))
def test_template(): t = template(parse(GOA)); assert "Riya" in t and "Dev" in t
def test_template_quiet(): assert "Nothing urgent" in template(parse("10/19/26, 10:05 PM - Zoya: gn\n10/19/26, 10:06 PM - Hamza: gn"))
def test_fallback(): assert make(parse(GOA), llm=Fake("Neha booked everything for 500."))[1] == "template"
def test_model_ok(): assert make(parse(GOA), llm=Fake("Mostly the goa plan.\nTrain tickets wait for manav.\nNothing waiting."))[1] == "gemma"
