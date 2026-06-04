# Engine Development Notes

## Stable Baseline

Treat the current `garry_botsparov.py` as the stable baseline unless a future change passes the required checks below.

Current baseline characteristics:

- Normal `evaluate()` is used in negamax and quiescence static evaluation.
- `evaluate()` uses bitboard piece iteration instead of `board.piece_map()`.
- Quiescence searches legal evasions when the side to move is in check before applying a depth-zero static evaluation.
- Transposition table lookup and storage in `negamax()` are limited to remaining depth `>= 2`.
- Killer moves are kept as the current move-ordering experiment.
- King safety remains controlled by `USE_KING_SAFETY`.

## Current Strongest Quick-Check Version

Quick-check results:

- Quick check passed: yes
- Repeated known blunders: 4
- Matched report Stockfish best: 4
- Position suite Stockfish matches: 11/27
- Average depth: 3.96
- Average time: 1.92s
- Average nodes: 16129
- Average TT hits: 763.59
- Average aspiration re-searches: 0.00

Decision: this is the current strongest development version by quick-check results.

Configuration:

- `ASPIRATION_WINDOW = None`
- TT behaviour restored/unchanged
- Iterative-deepening time guard kept
- Quiescence in-check fix kept
- Passed-pawn evaluation kept provisionally

## Experiments Kept For Now

### Phase-Specific Tuned Evaluation Weights

Constrained phase-specific tuning was applied.

Evaluation result after applying:

- MAE: 341.90
- RMSE: 584.09
- Correlation: 0.4966
- Sign agreement: 64.1%

Conversion test:

- Passed: yes
- Promotion occurred: yes

Quick check:

- Passed: yes
- Repeated known blunders: 4
- Matched report Stockfish best: 4
- Position suite matches: 10/27
- Average depth: 3.67
- Average time: 1.58s
- Average nodes: 12844
- Average TT hits: 580.22

Decision: keep as the current tuning candidate because it improves static evaluation alignment, preserves promotion conversion, and improves the quick-check position suite from 9/27 to 10/27.

### Passed-Pawn Evaluation Experiment

Quick-check results:

- Quick check passed: yes
- Repeated known blunders: 4
- Matched report Stockfish best: 4
- Position suite Stockfish matches: 11/27
- Average depth: 3.96
- Average time: 1.92s
- Average nodes: 16129
- Average TT hits: 763.59
- Average aspiration re-searches: 0.00
- Index 26 unchanged: Garry still chose `g1g5`

Position-suite comparison:

- Improved indices: 18 and 25
- Worsened indices by Stockfish-match status: none found
- Improvement is mixed: one endgame/pawn-related improvement and one middlegame/tactical improvement

Decision: keep passed-pawn evaluation provisionally as the current strongest quick-check version because it improved quick-check score without worsening blunders.

Note: this did not fix the manual rook/pawn conversion issue, so that needs separate investigation later.

Manual validation note:

- A manual rook/pawn endgame test was set up using this FEN:
  `8/2b5/8/3R4/8/5k2/1P3P1P/6K1 w - - 0 1`
- Garry playing White now pushes pawns and promotes instead of endlessly moving the rook/checking.
- This supports keeping the passed-pawn evaluation term.

Quick-check result for this version:

- Quick check passed: yes
- Repeated known blunders: 4
- Matched report Stockfish best: 4
- Position suite Stockfish matches: 11/27
- Average depth: 3.96
- Average time: 1.92s
- Average nodes: 16129
- Average TT hits: 763.59
- Aspiration re-searches: 0.00

Decision: passed-pawn evaluation is kept as part of the current v0.3.2 candidate.

### Aspiration Windows Disabled

Previous quick check with aspiration windows enabled:

- Repeated known blunders: 5
- Matched report Stockfish best: 3
- Position suite matches: 7/27
- Average depth: 4.30
- Average time: 1.80s
- Average nodes: 18361
- Average TT hits: 881.48
- Average aspiration re-searches: 0.85

After disabling aspiration windows:

- Repeated known blunders: 4
- Matched report Stockfish best: 4
- Position suite matches: 8/27
- Average depth: 4.22
- Average time: 1.86s
- Average nodes: 19032
- Average TT hits: 830.33
- Average aspiration re-searches: 0.00

Decision: keep `ASPIRATION_WINDOW = None` for now because it improves the quick-check metrics and removes wasted re-searches.

## Experiments Tried And Reverted

- Terminal detection refactor using pre-generated legal move lists in `negamax()` and `quiescence_search()`.
  It increased repeated known blunders and raised legal move generation time.

- Material-only quiescence leaf evaluation.
  It was faster in profile but hurt the short benchmark score and Stockfish-best matching.

- Reduced time-check overhead with `TIME_CHECK_INTERVAL`.
  It did not improve quality metrics and allowed average move time to exceed the 2.00s limit.

## Development Rule

Do not accept engine changes based only on depth, node count, or profile timing.

Depth and nodes are useful diagnostics, but benchmark quality and tactical regression behavior matter more.

## Required Checks Before Full Benchmark

Future engine changes must pass:

```powershell
& E:/Anaconda/python.exe "Garry Botsparov/test_quiescence.py"
& E:/Anaconda/python.exe "Garry Botsparov/test_blunders.py"
& E:/Anaconda/python.exe "Garry Botsparov/test_position_suite.py"
```

Only after those pass should a longer Stockfish benchmark be run.
