import math
import time

import chess
import chess.engine

from garry_botsparov import ChessEngine


STOCKFISH_PATH = r"C:\Users\Tom Greenwood\Desktop\Coding Projects\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"

STOCKFISH_ELO = 1500
NUM_GAMES = 5
MAX_PLIES = 200

YOUR_ENGINE_MAX_DEPTH = 10
YOUR_ENGINE_TIME_PER_MOVE = 2.0
STOCKFISH_TIME_PER_MOVE = 0.1


def play_game(stockfish, your_colour):
    board = chess.Board()

    # create a fresh engine for each game so the transposition table does not carry over
    your_engine = ChessEngine(
        max_depth=YOUR_ENGINE_MAX_DEPTH,
        time_limit=YOUR_ENGINE_TIME_PER_MOVE,
    )

    while not board.is_game_over(claim_draw=True) and board.ply() < MAX_PLIES:
        if board.turn == your_colour:
            move = your_engine.choose_move(board)
        else:
            result = stockfish.play(
                board,
                chess.engine.Limit(time=STOCKFISH_TIME_PER_MOVE),
            )
            move = result.move

        if move is None:
            break

        if move not in board.legal_moves:
            print(f"Illegal move attempted: {move}")
            print(board)
            break

        board.push(move)

    result = board.result(claim_draw=True)

    if result == "1-0":
        winner = chess.WHITE
    elif result == "0-1":
        winner = chess.BLACK
    else:
        winner = None

    if winner is None:
        return "draw", board.ply(), result

    if winner == your_colour:
        return "win", board.ply(), result

    return "loss", board.ply(), result


def score_results(results):
    wins = results.count("win")
    draws = results.count("draw")
    losses = results.count("loss")

    total = len(results)
    score = wins + 0.5 * draws
    score_rate = score / total if total > 0 else 0

    return wins, draws, losses, score, score_rate


def estimate_elo_difference(score_rate):
    if score_rate <= 0:
        return -999

    if score_rate >= 1:
        return 999

    return -400 * math.log10(1 / score_rate - 1)


def main():
    results = []

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as stockfish:
        stockfish.configure({
            "UCI_LimitStrength": True,
            "UCI_Elo": STOCKFISH_ELO,
        })

        start_time = time.time()

        for game_number in range(1, NUM_GAMES + 1):
            your_colour = chess.WHITE if game_number % 2 == 1 else chess.BLACK
            colour_name = "White" if your_colour == chess.WHITE else "Black"

            print(f"Game {game_number}/{NUM_GAMES}: your engine as {colour_name}")

            result, plies, raw_result = play_game(stockfish, your_colour)

            results.append(result)

            print(f"  result: {result} ({raw_result}), plies: {plies}")

        elapsed = time.time() - start_time

    wins, draws, losses, score, score_rate = score_results(results)
    elo_diff = estimate_elo_difference(score_rate)

    print()
    print("Benchmark complete")
    print("------------------")
    print(f"Your engine max depth: {YOUR_ENGINE_MAX_DEPTH}")
    print(f"Your engine time per move: {YOUR_ENGINE_TIME_PER_MOVE:.2f}s")
    print(f"Stockfish Elo setting: {STOCKFISH_ELO}")
    print(f"Stockfish time per move: {STOCKFISH_TIME_PER_MOVE:.2f}s")
    print(f"Games: {NUM_GAMES}")
    print(f"Wins: {wins}")
    print(f"Draws: {draws}")
    print(f"Losses: {losses}")
    print(f"Score: {score}/{NUM_GAMES}")
    print(f"Score rate: {100 * score_rate:.1f}%")

    if score_rate == 1:
        print("Estimated Elo difference: higher than this setting, not enough losses/draws to estimate.")
    elif score_rate == 0:
        print("Estimated Elo difference: lower than this setting, no score achieved.")
    else:
        print(f"Estimated Elo difference vs Stockfish setting: {elo_diff:+.0f}")

    print(f"Total time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()