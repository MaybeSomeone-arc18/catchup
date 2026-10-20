# catchup

a short morning brief for the group chats you didn't read. runs on your own machine, offline, free.

you export a chat, catchup reads it and hands back a few lines: what it was about, what was decided, which questions are still open. built for hacktoberfest week 3 ("slow and steady").

## why open

- your chats never leave your laptop. no server, no account, no upload.
- it runs a small open-weight model (gemma 3 1b, gguf) through llama.cpp. swap the file for any other gguf, nothing else changes.
- it costs nothing to run.

## how it works

rules pick what matters, the model only writes prose, and a checker guards the result.

1. `catchup/parser.py` reads a whatsapp export, drops system lines, joins wrapped lines, flags media.
2. `catchup/questions.py` scores messages with plain rules (question marks, question words, dates, plan words, your name).
3. `catchup/brief.py` gives the picked lines to the local model and asks for at most 3 short lines.
4. the checker compares every name, number and date in the answer with the chat. if something isn't in the source, the answer is dropped and a plain extractive brief is printed instead.

## what was measured (honest numbers)

4 synthetic chats (`samples/`, written by hand, 3 to 19 messages), gemma 3 1b q4_k_m, 2 cores, 2 GB RAM, llama-cpp-python 0.3.36:

- 3 of 4 model briefs passed the source check, 1 was rejected and replaced by the template.
- median 7.1 s, max 8.8 s per brief.
- the checker only catches invented names and numbers. i read the 3 passing briefs against the chats myself: one was vague but fine, two contained wrong claims (for example it said Ma called Didi, but Rohan did). so passing the check does not mean the brief is right.
- raw output: `eval/results_gemma3-1b-q4.json`.

## limits

- 4 tiny synthetic chats, no real private chats, no field use.
- a 1b model is weak at "who did what". the rule-picked lines are the part to trust.
- only the `d/m/yy, h:mm am - name: text` export shape is parsed.

## run it

```
pip install llama-cpp-python
python -m catchup chat.txt --you "your name" --model gemma-3-1b-it-Q4_K_M.gguf
python -m pytest -q                              # 15 tests
python eval/run_eval.py MODEL.gguf label         # re-run the numbers
```

without `--model` it prints the template brief and never touches a model.

built with an AI coding agent (disclosed in the dev.to post).
