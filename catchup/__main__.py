import argparse, sys, time
from .parser import parse
from .brief import make
from .digest import render
def main():
    p = argparse.ArgumentParser(prog="catchup", description="Two-line morning brief for a chat export, on your own machine.")
    p.add_argument("export"); p.add_argument("--you", default=""); p.add_argument("--model"); p.add_argument("--v1", action="store_true", help="old model-only brief")
    a = p.parse_args()
    chat = parse(open(a.export, encoding="utf-8", errors="replace").read())
    if not chat.human: sys.exit("no readable messages in that export")
    llm = None
    if a.model:
        from llama_cpp import Llama
        llm = Llama(model_path=a.model, n_ctx=2048, n_threads=2, verbose=False)
    t = time.time(); brief, src = make(chat, a.you, llm) if a.v1 else render(chat, llm, a.you)
    print(brief); print(f"\n[{src}, {len(chat.human)} messages, {time.time()-t:.1f}s]", file=sys.stderr)
if __name__ == "__main__": main()
