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
