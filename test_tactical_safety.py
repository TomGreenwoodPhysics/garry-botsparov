import json
from pathlib import Path

import chess
import chess.engine

from garry_botsparov import ChessEngine, PIECE_VALUES
from test_position_suite import (
    STOCKFISH_TIME_PER_POSITION,
    build_positions,
    get_stockfish,
)


OUTPUT_DIR = Path("analysis_games")
RESULTS_FILE = OUTPUT_DIR / "tactical_safety_results.jsonl"


def hanging_material(board, colour):
    total = 0
    hanging = []
    opponent = not colour

    for piece_type, value in PIECE_VALUES.items():
        if piece_type == chess.KING:
            continue

        for square in board.pieces(piece_type, colour):
            if board.attackers(opponent, square) and not board.attackers(colour, square):
                total += value
                hanging.append({
                    "square": chess.square_name(square),
                    "piece": chess.piece_name(piece_type),
                    "value": value,
                })

    return total, hanging


def free_capture_material(board):
    best_value = 0
    free_captures = []
    mover = board.turn
    opponent = not mover

    for move in board.legal_moves:
        if not board.is_capture(move):
            continue

        victim = board.piece_at(move.to_square)

        if victim is None and board.is_en_passant(move):
            victim = chess.Piece(chess.PAWN, opponent)

        if victim is None or victim.piece_type == chess.KING:
            continue

        if board.attackers(opponent, move.to_square):
            continue

        value = PIECE_VALUES[victim.piece_type]
        best_value = max(best_value, value)
        free_captures.append({
            "move": move.uci(),
            "piece": chess.piece_name(victim.piece_type),
            "value": value,
        })

    return best_value, free_captures


def stockfish_best_move(stockfish, board):
    if stockfish is None:
        return None

    result = stockfish.play(
        board,
        chess.engine.Limit(time=STOCKFISH_TIME_PER_POSITION),
    )
    return result.move


def analyse_position(position, stockfish, index):
    board = chess.Board(position["fen"])
    engine = ChessEngine()

    missed_free_capture_value, free_captures = free_capture_material(board)
    garry_move = engine.choose_move(board)
    stockfish_move = stockfish_best_move(stockfish, board)

    garry_hanging_value = None
    garry_hanging = []

    if garry_move is not None and garry_move in board.legal_moves:
        garry_board = board.copy(stack=False)
        garry_board.push(garry_move)
        garry_hanging_value, garry_hanging = hanging_material(garry_board, board.turn)

    stockfish_hanging_value = None
    stockfish_hanging = []

    if stockfish_move is not None and stockfish_move in board.legal_moves:
        stockfish_board = board.copy(stack=False)
        stockfish_board.push(stockfish_move)
        stockfish_hanging_value, stockfish_hanging = hanging_material(stockfish_board, board.turn)

    return {
        "index": index,
        "name": position["name"],
        "category": position.get("category"),
        "fen": position["fen"],
        "garry_move": garry_move.uci() if garry_move is not None else None,
        "stockfish_move": stockfish_move.uci() if stockfish_move is not None else None,
        "garry_hanging_material": garry_hanging_value,
        "garry_hanging_pieces": garry_hanging,
        "stockfish_hanging_material": stockfish_hanging_value,
        "stockfish_hanging_pieces": stockfish_hanging,
        "missed_free_capture_material": missed_free_capture_value,
        "available_free_captures": free_captures,
    }


def average(values):
    values = [value for value in values if value is not None]

    if not values:
        return None

    return sum(values) / len(values)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    RESULTS_FILE.write_text("", encoding="utf-8")

    positions = build_positions()
    stockfish = get_stockfish()
    results = []

    try:
        print(
            "idx | category | Garry | Stockfish | "
            "Garry hang | SF hang | missed free"
        )
        print("-" * 76)

        for index, position in enumerate(positions, start=1):
            result = analyse_position(position, stockfish, index)
            results.append(result)

            with open(RESULTS_FILE, "a", encoding="utf-8") as file:
                file.write(json.dumps(result) + "\n")

            stockfish_hanging = (
                result["stockfish_hanging_material"]
                if result["stockfish_hanging_material"] is not None
                else "n/a"
            )

            print(
                f"{result['index']:>3} | "
                f"{result['category'] or 'n/a':<10} | "
                f"{result['garry_move'] or 'None':<7} | "
                f"{result['stockfish_move'] or 'n/a':<9} | "
                f"{result['garry_hanging_material']!s:<10} | "
                f"{stockfish_hanging!s:<7} | "
                f"{result['missed_free_capture_material']}"
            )

    finally:
        if stockfish is not None:
            stockfish.quit()

    garry_average = average([
        result["garry_hanging_material"]
        for result in results
    ])
    stockfish_average = average([
        result["stockfish_hanging_material"]
        for result in results
    ])

    garry_worse_than_stockfish = sum(
        1 for result in results
        if (
            result["garry_hanging_material"] is not None
            and result["stockfish_hanging_material"] is not None
            and result["garry_hanging_material"] > result["stockfish_hanging_material"]
        )
    )
    missed_free_capture_positions = sum(
        1 for result in results
        if result["missed_free_capture_material"] >= PIECE_VALUES[chess.PAWN]
    )

    print()
    print("Summary")
    print("-------")
    print(f"Positions tested: {len(results)}")
    print(f"Average Garry hanging material: {garry_average:.2f}")

    if stockfish_average is None:
        print("Average Stockfish hanging material: unavailable")
    else:
        print(f"Average Stockfish hanging material: {stockfish_average:.2f}")

    print(
        "Garry leaves more hanging material than Stockfish: "
        f"{garry_worse_than_stockfish}"
    )
    print(
        "Positions with missed free capture worth at least a pawn: "
        f"{missed_free_capture_positions}"
    )


if __name__ == "__main__":
    main()
