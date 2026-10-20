# catchup

a short morning brief for the group chats you didn't read. runs on your own machine, offline, free.

you export a chat, catchup reads it and hands back a few lines: what it was about, what was decided, which questions are still open. built for hacktoberfest week 3 ("slow and steady").

## why open

- your chats never leave your laptop. no server, no account, no upload.
- it can use a small open-weight model (gemma 3 1b, gguf) through llama.cpp for one gist line. swap the file for any other gguf. without a model it still prints the digest.
- it costs nothing to run.

## how it works (v2)

the facts come straight from the chat. the model only gets to write one short gist, and a checker guards it.

1. `catchup/parser.py` reads a whatsapp export, drops system lines, joins wrapped lines, flags media.
2. `catchup/digest.py` picks up to 10 lines by plain rules (times, amounts, questions, plan words, your name) and prints them verbatim with who said them.
3. optional: the local model writes one sentence on what the chat is about, at temperature 0. the gist is dropped if it names a person, has a digit, runs past 24 words, spans lines, or fails the old name and number check. then only the digest prints.
4. a chat with no such lines prints "Nothing needs you."

v1 (model writes the whole brief, template fallback) is still there: `--v1`.

## what was measured (honest numbers)

metric: gold-string recall. for each chat i wrote down, before running, the strings a reader must not miss (a time, an amount, an open question). the score is how many appear, case-insensitive, in the output. it is a proxy. it does not grade whether a sentence is right.

gemma 3 1b q4_k_m, 2 cores, 2 GB RAM, llama-cpp-python 0.3.36, one run each:

| set | v1 (model writes brief) | v2 (digest + gist) |
|---|---|---|
| dev, 8 chats, 39 gold strings | 15/39 = 38.5%, median 7.2 s | 37/39 = 94.9%, median 4.0 s |
| held-out, 4 chats, 24 gold strings | 10/24 = 41.7%, median 7.8 s | 22/24 = 91.7%, median 3.4 s |

- the dev set is tuned: i saw its gold when i wrote the v2 rules. the held-out set was written after the rules were frozen and was not used to change them. only the held-out row is a fair test, and it is 4 chats.
- v2 misses: dev, goa-trip (`20:15`, `tickets`); held-out, office (`webhook`) and society (`lift`).
- the v1 numbers in the first version of this readme (3 of 4 passed the checker) came from 4 chats and another run. gemma is not fully repeatable between runs, so v1 differs a little between runs.
- gists are vague one-liners, and one or two are slightly off (family: it merges the cake and the plumber). v2's wrong-claim risk is lower because the lines are copied, not rewritten, but i did not measure it beyond reading them.
- raw output for this table: `eval/score_*.json`. `eval/results_gemma3-1b-q4.json` and `eval/run_eval.py` are the original first v1 run on the first 4 chats.

## limits

- 12 tiny synthetic chats (9 to 19 messages), all written by me. no real private chats, no field use.
- gold-string recall rewards copying lines, so v2 is built to score well on it. it says nothing on whether the brief is a nicer read.
- longer chats would hit the 10 line cap and the gist only sees the first 40 messages. not tested.
- no comparison with a larger or closed model.
- only the `d/m/yy, h:mm am - name: text` export shape is parsed.

## run it

```
pip install llama-cpp-python
python -m catchup chat.txt --you "your name"                      # rules digest only, no model
python -m catchup chat.txt --you "your name" --model gemma-3-1b-it-Q4_K_M.gguf   # digest + gist
python -m catchup chat.txt --model gemma-3-1b-it-Q4_K_M.gguf --v1 # old model-only brief
python -m pytest -q                                               # 23 tests
python eval/score.py MODEL.gguf label v2 heldout                  # v1|v2, dev|heldout
```

built with an AI coding agent (disclosed in the dev.to post).
