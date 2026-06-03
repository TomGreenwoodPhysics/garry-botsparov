# Garry Botsparov

A Python chess engine project featuring move generation, board evaluation, search, and benchmarking against Stockfish.

## Features

- Legal move generation
- Position evaluation with piece-square tables and king-safety terms
- Minimax/negamax search
- Alpha-beta pruning
- Iterative deepening with aspiration windows
- Transposition table support
- Quiescence search
- Optional Polyglot opening book support
- Stockfish benchmarking
- Game analysis and blunder-report tooling
- Pygame-based interface

## Current status

Project is under active development.

## Current benchmark

**Garry Botsparov v0.3.0** was benchmarked against Stockfish limited to 1550 Elo.

Across 30 games, it scored 17.0/30, with 13 wins, 8 draws, and 9 losses. This matches the v0.2.0 score, but the average search depth improved from approximately 3.95 plies to 4.48 plies under the same 2-second move limit.

Benchmark settings:

- Garry Botsparov: 2.0 seconds per move, maximum search depth 10
- Stockfish: 1550 Elo limit, 0.1 seconds per move
- Games: 30
- Average depth reached: 4.48 plies
- Maximum depth reached: 8 plies
- Average nodes per move: 33,161
- Opening book: disabled