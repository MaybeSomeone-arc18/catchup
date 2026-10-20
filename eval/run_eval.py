"""usage: python eval/run_eval.py MODEL.gguf label  -> latency + fallback-rate numbers"""
import json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from catchup.parser import parse
from catchup.brief import make
from llama_cpp import Llama
HERE = os.path.dirname(os.path.abspath(__file__))
llm = Llama(model_path=sys.argv[1], n_ctx=2048, n_threads=2, verbose=False)
rows = []
for fn in sorted(os.listdir(os.path.join(HERE, "..", "samples"))):
    if not fn.endswith(".txt"): continue
    raw = open(os.path.join(HERE, "..", "samples", fn), encoding="utf-8").read()
    chat = parse(raw); t = time.time(); brief, src = make(chat, llm=llm); dt = time.time() - t
    rows.append({"sample": fn, "messages": len(chat.human), "src": src, "secs": round(dt, 1), "brief": brief, "chat": raw})
    print(fn, src, round(dt, 1), flush=True)
n = len(rows); g = sum(r["src"] == "gemma" for r in rows)
summary = {"model": sys.argv[2], "samples": n, "gemma_valid": g, "fallback_to_template": n - g,
           "median_secs": round(statistics.median(r["secs"] for r in rows), 1), "max_secs": max(r["secs"] for r in rows)}
print(json.dumps(summary))
json.dump({"summary": summary, "rows": rows}, open(os.path.join(HERE, f"results_{sys.argv[2]}.json"), "w"), indent=1)
