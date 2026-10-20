"""Score a catchup version on the sample chats.
usage: python eval/score.py MODEL.gguf label v1|v2 dev|heldout
recall = share of gold strings (eval/gold.json, written before measuring) found in the final output text.
Short gold strings, case-insensitive substring match, so paraphrase can miss: that is strict on the model."""
import json, os, statistics, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from catchup.parser import parse
from llama_cpp import Llama
ver = sys.argv[3]
setname = sys.argv[4]
SAMPLES = os.path.join(ROOT, "samples") if setname == "dev" else os.path.join(ROOT, "samples", "heldout")
GOLD = os.path.join(ROOT, "eval", "gold.json" if setname == "dev" else "gold_heldout.json")
if ver == "v1":
    from catchup.brief import make
    def render(chat, llm): return make(chat, llm=llm)
else:
    from catchup.digest import render
gold = json.load(open(GOLD))
llm = Llama(model_path=sys.argv[1], n_ctx=2048, n_threads=2, verbose=False)
rows = []
for fn in sorted(gold):
    raw = open(os.path.join(SAMPLES, fn), encoding="utf-8").read()
    chat = parse(raw); t = time.time(); out, src = render(chat, llm); dt = time.time() - t
    hit = [g for g in gold[fn] if g.lower() in out.lower()]
    rows.append({"sample": fn, "src": src, "secs": round(dt, 1), "gold": len(gold[fn]), "hit": len(hit),
                 "missed": [g for g in gold[fn] if g not in hit], "output": out, "chat": raw})
    print(fn, src, round(dt, 1), f"{len(hit)}/{len(gold[fn])}", flush=True)
G = sum(r["gold"] for r in rows); H = sum(r["hit"] for r in rows)
s = {"version": ver, "set": setname, "model": sys.argv[2], "samples": len(rows), "gold_total": G, "gold_hit": H,
     "recall": round(H / G, 3), "model_used": sum(r["src"] == "gemma" for r in rows),
     "median_secs": round(statistics.median(r["secs"] for r in rows), 1)}
print(json.dumps(s))
json.dump({"summary": s, "rows": rows}, open(os.path.join(ROOT, "eval", f"score_{setname}_{ver}.json"), "w"), indent=1)
