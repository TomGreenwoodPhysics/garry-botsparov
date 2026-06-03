import json
from pathlib import Path

import chess
import chess.engine


STOCKFISH_PATH = r"C:\Users\Tom Greenwood\Desktop\Coding Projects\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"

MOVE_LOG_FILE = Path("analysis_games/garry_move_log.jsonl")
OUTPUT_FILE = Path("analysis_games/blunder_report.txt")

ANALYSIS_TIME = 0.5
TOP_N = 30


def score_to_cp(score, board):
    pov_score = score.pov(board.turn)

    if pov_score.is_mate():
        mate = pov_score.mate()

        if mate is None:
            return 0

        if mate > 0:
            return 100000 - mate

        return -100000 - mate

    return pov_score.score(mate_score=100000)


def analyse_move(stockfish, log):
    board = chess.Board(log["fen_before"])
    garry_move = chess.Move.from_uci(log["move"])

    before_info = stockfish.analyse(
        board,
        chess.engine.Limit(time=ANALYSIS_TIME),
    )

    best_move = before_info["pv"][0]
    best_eval = score_to_cp(before_info["score"], board)

    board.push(garry_move)

    after_info = stockfish.analyse(
        board,
        chess.engine.Limit(time=ANALYSIS_TIME),
    )

    after_eval = -score_to_cp(after_info["score"], board)

    loss = best_eval - after_eval

    return {
        "game": log["game"],
        "ply": log["ply"],
        "phase": log["phase"],
        "fen": log["fen_before"],
        "garry_move": log["move"],
        "best_move": best_move.uci(),
        "best_eval": best_eval,
        "after_eval": after_eval,
        "loss": loss,
        "depth": log["depth"],
        "nodes": log["nodes"],
        "time": log["time"],
        "tt_hits": log["tt_hits"],
        "result": log["result"],
    }


def load_move_logs():
    logs = []

    with open(MOVE_LOG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            log = json.loads(line)

            if log["move"] is not None:
                logs.append(log)

    return logs


def write_report(results):
    results = sorted(results, key=lambda item: item["loss"], reverse=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("Garry Botsparov blunder report\n")
        file.write("==============================\n\n")

        for index, result in enumerate(results[:TOP_N], start=1):
            file.write(f"{index}. Game {result['game']}, ply {result['ply']}\n")
            file.write(f"   Phase: {result['phase']}\n")
            file.write(f"   Result: {result['result']}\n")
            file.write(f"   Garry move: {result['garry_move']}\n")
            file.write(f"   Stockfish best: {result['best_move']}\n")
            file.write(f"   Eval before best move: {result['best_eval']} cp\n")
            file.write(f"   Eval after Garry move: {result['after_eval']} cp\n")
            file.write(f"   Estimated loss: {result['loss']} cp\n")
            file.write(f"   Garry search depth: {result['depth']}\n")
            file.write(f"   Garry nodes: {result['nodes']}\n")
            file.write(f"   FEN: {result['fen']}\n\n")


def main():
    logs = load_move_logs()
    results = []

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as stockfish:
        for index, log in enumerate(logs, start=1):
            print(f"Analysing Garry move {index}/{len(logs)}")

            try:
                results.append(analyse_move(stockfish, log))
            except Exception as error:
                print(f"  skipped move due to error: {error}")

    write_report(results)

    print()
    print(f"Report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()