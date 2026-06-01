# Garry Botsparov

A Python chess engine project featuring move generation, board evaluation, search, and benchmarking against Stockfish.

## Features

- Legal move generation
- Position evaluation
- Minimax/negamax search
- Alpha-beta pruning
- Stockfish benchmarking
- Pygame-based interface

## Current status

Project is under active development.

## Current benchmark

**Garry Botsparov v0.2.0** was benchmarked against Stockfish limited to 1550 Elo.

Across 30 games, Garry Botsparov scored 17.0/30, with 13 wins, 8 draws, and 9 losses. This corresponds to an estimated strength of approximately **1600 ± 110 Elo at 95% confidence** under the benchmark settings.

Benchmark settings:

- Garry Botsparov: 2.0 seconds per move, maximum search depth 10
- Stockfish: 1550 Elo limit, 0.1 seconds per move
- Games: 30
- Average depth reached: approximately 3.95 plies
- Maximum depth reached: 8 plies

This estimate is approximate because it is based on a limited 30-game sample and depends on the chosen Stockfish time and Elo settings.