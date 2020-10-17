# othelloAI
Making an Othello AI bot.

![screenshot](othelloAI.png)

This was done as part of an AI course that delved into implementing algorithms for various AI problems. For this, I developed an ai Othello agent (aptly, `ai_agent.py`), which would be the brains for an Human (or Ai) vs AI bot match.

The agent uses various strategies for calculating its optimal next move - MiniMax and AlphaBeta pruning (with depth limiting) to look ahead at possible moves, state caching to reduce redundant calculations, and the development of node ordering heuristics to optimize choices. This provided an incredibly challenging opposition bot.

## Run
simply run the shell script `run.sh`.

This makes the call:
`python3 othello_gui.py -d 8 -a ai_agent.py -c -o -l 6`
`-d`: board size (ie 8x8)
`-a`: agent file location
`-c`: use caching
`-o`: use ordering heuristics
`-l`: depth limit (ie depth of 6). Reduce for less processing time and "easier" opponent.
