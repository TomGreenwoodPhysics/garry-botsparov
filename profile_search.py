import cProfile
import io
import pstats

import chess

from garry_botsparov import ChessEngine


FENS = [
    chess.STARTING_FEN,
    "r1bq1rk1/ppp2ppp/2np1n2/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 2 7",
    "r4rk1/3q1ppp/2n5/1P6/8/1p1PN3/1PK1P1P1/R1BQ1B1R w - - 0 26",
    "5k1r/3qp3/1b3p2/8/4PP2/2P4r/PP1PQ1KP/R1B4R w - - 5 40",
    "r1b1qk2/ppppp2B/8/7p/2P4Q/8/PPPK4/R5b1 b - - 2 25",
]


def run_profile():
    engine = ChessEngine()

    for fen in FENS:
        board = chess.Board(fen)
        engine.choose_move(board)


def main():
    profiler = cProfile.Profile()
    profiler.enable()
    run_profile()
    profiler.disable()

    output = io.StringIO()
    stats = pstats.Stats(profiler, stream=output)
    stats.strip_dirs()
    stats.sort_stats("cumtime")
    stats.print_stats(25)

    print(output.getvalue())


if __name__ == "__main__":
    main()
