# catchup

a short morning brief for the group chats you didn't read. runs on your own machine, offline, free.

you export a chat, catchup reads it and hands back a few lines: what it was about, what was decided, which questions are still open. built for hacktoberfest week 3 ("slow and steady").

## why open

- your chats never leave your laptop. no server, no account, no upload.
- it can use a small open-weight model (gemma 3 1b, gguf) through llama.cpp for one gist line. swap the file for any other gguf. without a model it still prints the digest.
- it costs nothing to run.

## how it works (v3)

the facts come straight from the chat. the model only gets to write one short gist, and a checker guards it.

1. `catchup/parser.py` reads a whatsapp export, drops system lines, joins wrapped lines, flags media.
2. `catchup/digest.py` picks up to 12 lines by plain rules (times, amounts, questions, plan words, problem words like "stuck" or "out of", your name) and prints them verbatim with who said them.
3. optional: the local model writes one sentence on what the chat is about, at temperature 0. the gist is dropped if it names a person, has a digit, runs past 24 words, spans lines, or fails the old name and number check. then only the digest prints.
4. a chat with no such lines prints "Nothing needs you."

v1 (model writes the whole brief, template fallback) is still there: `--v1`.

## what was measured (honest numbers)

metric: gold-string recall. for each chat i wrote down, before running, the strings a reader must not miss (a time, an amount, an open question). the score is how many appear, case-insensitive, in the output. it is a proxy. it does not grade whether a sentence is right.

gemma 3 1b q4_k_m, 2 cores, 2 GB RAM, llama-cpp-python 0.3.36, one run per cell.

| set | v1 model-only | v2 digest + gist | v3 (v2 + problem words, cap 12) |
|---|---|---|---|
| dev, 8 chats, 39 gold (tuned on) | 15/39 = 38.5% | 37/39 = 94.9% | 38/39 = 97.4% |
| set C, 4 chats, 24 gold (v2 misses seen, so used) | 10/24 = 41.7% | 22/24 = 91.7% | 24/24 = 100% |
| set D, 4 chats, 20 gold (fresh, gold frozen before any run), before the parser fix | 6/20 = 30% | 18/20 = 90% | 18/20 = 90% |
| set D after the parser fix (now used) | 6/20 | 19/20 | 19/20 |

- the only fair row is set D before the parser fix: 4 chats, 20 gold strings, one run. there v2 and v3 are equal. the v3 gains on dev and C come from rules i wrote after seeing those misses, so they do not count as evidence.
- set D found a real bug: the parser dropped any chat message containing the word "left" (as in "i left them at home") as a system line. fixed (system lines are only lines with no sender) and tested. that fix moved D from 18/20 to 19/20, but D was already seen by then.
- remaining misses: `tickets` (dev, goa-trip, over the line cap) and `compressor` (D, a statement with no time, question or problem word).
- median time: v1 6.4 to 7.8 s, v2 and v3 3.5 to 4.0 s.
- length: v3 prints up to 12 lines. on an 18 or 19 message chat that is 12 lines, so it is not much shorter than the chat. on 9 to 13 message chats it prints 5 to 10 lines. i have not tested long chats.
- gemma is not fully repeatable between runs, so v1 moves a little each time. the first version of this readme said 3 of 4 passed the checker on 4 chats, from an earlier run.
- gists are vague one-liners and can be slightly off. the verbatim lines are the part to trust.
- raw output: `eval/score_*.json`; D before the parser fix is in `eval/prefix/`; the D files and gold are fixed by `eval/d_frozen_sha1.txt`. `eval/results_gemma3-1b-q4.json` and `eval/run_eval.py` are the original first v1 run.

## limits

- 16 tiny synthetic chats (3 to 19 messages), all written by me. no real private chats, no field use.
- gold-string recall rewards copying lines, so the digest is built to score well on it. it says nothing on whether the brief is a nicer read.
- the gist only sees the first 40 messages. long chats are untested.
- no comparison with a larger or closed model.
- only the `d/m/yy, h:mm am - name: text` export shape is parsed.

## run it

```
pip install llama-cpp-python
python -m catchup chat.txt --you "your name"                      # rules digest only, no model
python -m catchup chat.txt --you "your name" --model gemma-3-1b-it-Q4_K_M.gguf   # digest + gist
python -m catchup chat.txt --model gemma-3-1b-it-Q4_K_M.gguf --v1 # old model-only brief
python -m pytest -q                                               # 26 tests
python eval/score.py MODEL.gguf label v3 heldout_d                 # v1|v2|v3, dev|heldout|heldout_d
```

built with an AI coding agent (disclosed in the dev.to post).
