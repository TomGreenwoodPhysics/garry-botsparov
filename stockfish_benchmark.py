import json
import math
import time
from pathlib import Path

import chess
import chess.engine
import chess.pgn

from garry_botsparov import ChessEngine


STOCKFISH_PATH = r"C:\Users\Tom Greenwood\Desktop\Coding Projects\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"

STOCKFISH_ELO = 1550
NUM_GAMES = 30
MAX_PLIES = 400

YOUR_ENGINE_MAX_DEPTH = 10
YOUR_ENGINE_TIME_PER_MOVE = 2.0
STOCKFISH_TIME_PER_MOVE = 0.1

OUTPUT_DIR = Path("analysis_games")
PGN_FILE = OUTPUT_DIR / "benchmark_games.pgn"
MOVE_LOG_FILE = OUTPUT_DIR / "garry_move_log.jsonl"


def get_game_phase(ply):
    if ply < 20:
        return "opening"

    if ply < 80:
        return "middlegame"

    return "endgame"


def save_game_pgn(board, game_number, your_colour, result):
    game = chess.pgn.Game.from_board(board)

    game.headers["Event"] = "Garry Botsparov Benchmark"
    game.headers["Round"] = str(game_number)
    game.headers["White"] = "Garry Botsparov" if your_colour == chess.WHITE else "Stockfish"
    game.headers["Black"] = "Garry Botsparov" if your_colour == chess.BLACK else "Stockfish"
    game.headers["Result"] = result
    game.headers["StockfishElo"] = str(STOCKFISH_ELO)
    game.headers["GarryTimePerMove"] = f"{YOUR_ENGINE_TIME_PER_MOVE:.2f}"
    game.headers["StockfishTimePerMove"] = f"{STOCKFISH_TIME_PER_MOVE:.2f}"
    game.headers["GarryMaxDepth"] = str(YOUR_ENGINE_MAX_DEPTH)

    with open(PGN_FILE, "a", encoding="utf-8") as file:
        print(game, file=file, end="\n\n")


def play_game(stockfish, your_colour, game_number):
    board = chess.Board()

    # fresh engine each game so the transposition table does not carry over
    your_engine = ChessEngine(
        max_depth=YOUR_ENGINE_MAX_DEPTH,
        time_limit=YOUR_ENGINE_TIME_PER_MOVE,
    )

    move_stats = []
    garry_move_logs = []

    while not board.is_game_over(claim_draw=True) and board.ply() < MAX_PLIES:
        if board.turn == your_colour:
            phase = get_game_phase(board.ply())
            fen_before = board.fen()
            move = your_engine.choose_move(board)

            move_stats.append({
                "depth": your_engine.last_depth_reached,
                "nodes": your_engine.nodes_searched,
                "time": your_engine.last_search_time,
                "tt_hits": your_engine.tt_hits,
                "phase": phase,
            })

            log_entry = {
                "game": game_number,
                "ply": board.ply(),
                "fen_before": fen_before,
                "move": move.uci() if move is not None else None,
                "phase": phase,
                "depth": your_engine.last_depth_reached,
                "nodes": your_engine.nodes_searched,
                "time": your_engine.last_search_time,
                "tt_hits": your_engine.tt_hits,
                "your_colour": "white" if your_colour == chess.WHITE else "black",
            }

            if hasattr(your_engine, "aspiration_researches"):
                log_entry["aspiration_researches"] = your_engine.aspiration_researches

            garry_move_logs.append(log_entry)

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

    save_game_pgn(board, game_number, your_colour, result)

    with open(MOVE_LOG_FILE, "a", encoding="utf-8") as file:
        for log in garry_move_logs:
            log["result"] = result
            file.write(json.dumps(log) + "\n")

    if result == "1-0":
        winner = chess.WHITE
    elif result == "0-1":
        winner = chess.BLACK
    else:
        winner = None

    if winner is None:
        return "draw", board.ply(), result, move_stats

    if winner == your_colour:
        return "win", board.ply(), result, move_stats

    return "loss", board.ply(), result, move_stats


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


def average(values):
    if not values:
        return 0

    return sum(values) / len(values)


def summarise_search_stats(all_move_stats):
    depths = [stat["depth"] for stat in all_move_stats]
    nodes = [stat["nodes"] for stat in all_move_stats]
    times = [stat["time"] for stat in all_move_stats]
    tt_hits = [stat["tt_hits"] for stat in all_move_stats]

    phase_depths = {
        "opening": [],
        "middlegame": [],
        "endgame": [],
    }

    for stat in all_move_stats:
        phase_depths[stat["phase"]].append(stat["depth"])

    return {
        "moves": len(all_move_stats),
        "avg_depth": average(depths),
        "max_depth": max(depths) if depths else 0,
        "avg_nodes": average(nodes),
        "avg_time": average(times),
        "avg_tt_hits": average(tt_hits),
        "phase_depths": {
            phase: average(depth_list)
            for phase, depth_list in phase_depths.items()
        },
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    PGN_FILE.write_text("", encoding="utf-8")
    MOVE_LOG_FILE.write_text("", encoding="utf-8")

    results = []
    all_move_stats = []

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

            result, plies, raw_result, move_stats = play_game(
                stockfish,
                your_colour,
                game_number,
            )

            results.append(result)
            all_move_stats.extend(move_stats)

            game_avg_depth = average([stat["depth"] for stat in move_stats])
            game_avg_time = average([stat["time"] for stat in move_stats])

            print(f"  result: {result} ({raw_result}), plies: {plies}")
            print(f"  average depth: {game_avg_depth:.2f}")
            print(f"  average time/move: {game_avg_time:.2f}s")

        elapsed = time.time() - start_time

    wins, draws, losses, score, score_rate = score_results(results)
    elo_diff = estimate_elo_difference(score_rate)
    search_stats = summarise_search_stats(all_move_stats)

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

    print()
    print("Engine search stats")
    print("-------------------")
    print(f"Engine moves analysed: {search_stats['moves']}")
    print(f"Average depth reached: {search_stats['avg_depth']:.2f}")
    print(f"Maximum depth reached: {search_stats['max_depth']}")
    print(f"Average nodes per move: {search_stats['avg_nodes']:.0f}")
    print(f"Average time per move: {search_stats['avg_time']:.2f}s")
    print(f"Average TT hits per move: {search_stats['avg_tt_hits']:.0f}")

    print()
    print("Average depth by phase")
    print("----------------------")
    print(f"Opening: {search_stats['phase_depths']['opening']:.2f}")
    print(f"Middlegame: {search_stats['phase_depths']['middlegame']:.2f}")
    print(f"Endgame: {search_stats['phase_depths']['endgame']:.2f}")

    print()
    print("Analysis files written")
    print("----------------------")
    print(f"PGN: {PGN_FILE}")
    print(f"Move log: {MOVE_LOG_FILE}")


if __name__ == "__main__":
    main()
