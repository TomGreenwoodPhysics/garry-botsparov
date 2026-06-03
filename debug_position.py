import time

import chess
import chess.engine

from garry_botsparov import ChessEngine, SearchTimeout


STOCKFISH_PATH = r"C:\Users\Tom Greenwood\Desktop\Coding Projects\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"

FEN = "r1b4r/pppp2qk/4p3/4P3/3P1R1Q/2n4P/6P1/7K b - - 1 37"

KNOWN_BAD_MOVE = "g7h6"
STOCKFISH_BEST_FROM_REPORT = "h7g6"

# engine diagnostic settings
ENGINE_DEPTH = 4
TIME_PER_ROOT_MOVE = 5.0

# Stockfish diagnostic settings
STOCKFISH_ANALYSIS_TIME = 0.3
STOCKFISH_COMPARE_TOP_N = 10


def score_to_cp(score, board):
    score = score.pov(board.turn)

    if score.is_mate():
        mate = score.mate()

        if mate is None:
            return 0

        if mate > 0:
            return 100000 - mate

        return -100000 - mate

    return score.score(mate_score=100000)


def analyse_stockfish_best(stockfish, board):
    info = stockfish.analyse(
        board,
        chess.engine.Limit(time=STOCKFISH_ANALYSIS_TIME),
    )

    best_move = info["pv"][0]
    best_score = score_to_cp(info["score"], board)

    return best_move, best_score


def analyse_stockfish_forced_move(stockfish, board, move):
    info = stockfish.analyse(
        board,
        chess.engine.Limit(time=STOCKFISH_ANALYSIS_TIME),
        root_moves=[move],
    )

    return score_to_cp(info["score"], board)


def get_garry_chosen_move(board):
    engine = ChessEngine(max_depth=10, time_limit=2.0)
    move = engine.choose_move(board)

    return {
        "move": move,
        "eval": engine.last_eval,
        "depth": engine.last_depth_reached,
        "nodes": engine.nodes_searched,
        "tt_hits": engine.tt_hits,
        "time": engine.last_search_time,
    }


def score_root_move(board, move, depth):
    engine = ChessEngine(max_depth=depth, time_limit=TIME_PER_ROOT_MOVE)

    engine.nodes_searched = 0
    engine.tt_hits = 0
    engine.aspiration_researches = 0
    engine.last_depth_reached = 0
    engine.search_start_time = time.time()

    board.push(move)

    try:
        score = -engine.negamax(
            board,
            depth - 1,
            -float("inf"),
            float("inf"),
        )
        timed_out = False
    except SearchTimeout:
        score = None
        timed_out = True
    finally:
        board.pop()

    elapsed = time.time() - engine.search_start_time

    return {
        "move": move,
        "score": score,
        "timed_out": timed_out,
        "nodes": engine.nodes_searched,
        "tt_hits": engine.tt_hits,
        "time": elapsed,
    }


def rank_garry_root_moves(board):
    engine = ChessEngine(max_depth=ENGINE_DEPTH, time_limit=TIME_PER_ROOT_MOVE)
    tt_move = engine.get_tt_move(board)
    ordered_moves = engine.order_moves(board, list(board.legal_moves), tt_move)

    results = []

    for index, move in enumerate(ordered_moves, start=1):
        result = score_root_move(board, move, ENGINE_DEPTH)
        result["order"] = index
        results.append(result)

    completed = [
        result for result in results
        if result["score"] is not None
    ]

    completed.sort(key=lambda item: item["score"], reverse=True)

    timed_out = [
        result for result in results
        if result["score"] is None
    ]

    return completed, timed_out


def print_board_info(board):
    print("Position")
    print("--------")
    print(board)
    print()
    print(f"FEN: {board.fen()}")
    print(f"Side to move: {'White' if board.turn == chess.WHITE else 'Black'}")
    print(f"Legal moves: {board.legal_moves.count()}")
    print()


def print_garry_choice(board):
    chosen = get_garry_chosen_move(board)

    print("Garry normal choose_move()")
    print("--------------------------")
    print(f"Garry move: {chosen['move']}")
    print(f"Garry eval: {chosen['eval']:.2f} pawns")
    print(f"Depth reached: {chosen['depth']}")
    print(f"Nodes: {chosen['nodes']}")
    print(f"TT hits: {chosen['tt_hits']}")
    print(f"Time: {chosen['time']:.2f}s")
    print()

    return chosen["move"]


def print_stockfish_summary(stockfish, board, garry_move):
    stockfish_best, stockfish_best_eval = analyse_stockfish_best(stockfish, board)

    print("Stockfish summary")
    print("-----------------")
    print(f"Stockfish best: {stockfish_best}")
    print(f"Stockfish eval for best: {stockfish_best_eval} cp")
    print(f"Report best: {STOCKFISH_BEST_FROM_REPORT}")
    print(f"Known bad move: {KNOWN_BAD_MOVE}")

    if garry_move is not None:
        garry_forced_eval = analyse_stockfish_forced_move(stockfish, board, garry_move)
        loss = stockfish_best_eval - garry_forced_eval

        print(f"Stockfish eval for Garry move {garry_move}: {garry_forced_eval} cp")
        print(f"Estimated loss: {loss} cp")

    print()

    return stockfish_best

def print_garry_by_depth(board):
    print("Garry choose_move by max depth")
    print("------------------------------")

    for depth in range(1, 7):
        engine = ChessEngine(max_depth=depth, time_limit=2.0)
        move = engine.choose_move(board)

        print(
            f"max_depth {depth}: move {move}, "
            f"eval {engine.last_eval:.2f}, "
            f"depth reached {engine.last_depth_reached}, "
            f"nodes {engine.nodes_searched}, "
            f"time {engine.last_search_time:.2f}s"
        )

    print()

def print_root_ranking(board, stockfish=None):
    completed, timed_out = rank_garry_root_moves(board)

    print(f"Garry root move scores at fixed depth {ENGINE_DEPTH}")
    print("-------------------------------------------")
    print(
        f"{'rank':>4}  {'ord':>4}  {'move':>6}  {'garry cp':>9}  "
        f"{'nodes':>8}  {'time':>6}  {'sf cp':>8}  notes"
    )

    for rank, result in enumerate(completed, start=1):
        move = result["move"]
        garry_score = result["score"]
        sf_score_text = ""

        if stockfish is not None and rank <= STOCKFISH_COMPARE_TOP_N:
            try:
                sf_score = analyse_stockfish_forced_move(stockfish, board, move)
                sf_score_text = str(sf_score)
            except Exception:
                sf_score_text = "err"

        notes = []

        if move.uci() == KNOWN_BAD_MOVE:
            notes.append("known bad")

        if move.uci() == STOCKFISH_BEST_FROM_REPORT:
            notes.append("report best")

        print(
            f"{rank:>4}  {result['order']:>4}  {move.uci():>6}  "
            f"{garry_score:>9}  {result['nodes']:>8}  "
            f"{result['time']:>6.2f}  {sf_score_text:>8}  "
            f"{', '.join(notes)}"
        )

    if timed_out:
        print()
        print("Timed-out root moves")
        print("--------------------")

        for result in timed_out:
            print(
                f"order {result['order']:>2}: {result['move']} "
                f"after {result['time']:.2f}s, nodes {result['nodes']}"
            )

    print()


def main():
    board = chess.Board(FEN)

    print_board_info(board)
    print_garry_by_depth(board)
    garry_move = print_garry_choice(board)

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as stockfish:
        print_stockfish_summary(stockfish, board, garry_move)
        print_root_ranking(board, stockfish)


if __name__ == "__main__":
    main()