import json
from pathlib import Path

import chess
import chess.engine

from garry_botsparov import ChessEngine

try:
    from test_blunders import STOCKFISH_PATH, TEST_POSITIONS as BLUNDER_POSITIONS
except ImportError:
    STOCKFISH_PATH = None
    BLUNDER_POSITIONS = []


OUTPUT_DIR = Path("analysis_games")
RESULTS_FILE = OUTPUT_DIR / "position_suite_results.jsonl"
STOCKFISH_TIME_PER_POSITION = 0.1


EXTRA_POSITIONS = [
    {
        "name": "Opening: initial position",
        "category": "opening",
        "fen": chess.STARTING_FEN,
    },
    {
        "name": "Opening: Italian development",
        "category": "opening",
        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 3",
    },
    {
        "name": "Opening: Queen's Gambit structure",
        "category": "opening",
        "fen": "rnbqkbnr/pp2pppp/2p5/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3",
    },
    {
        "name": "Opening: Sicilian development",
        "category": "opening",
        "fen": "r1bqkbnr/pp1ppppp/2n5/2p5/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 2 4",
    },
    {
        "name": "Opening: Caro-Kann advance",
        "category": "opening",
        "fen": "rnbqkbnr/pp2pppp/2p5/3pP3/8/8/PPPP1PPP/RNBQKBNR w KQkq - 0 3",
    },
    {
        "name": "Middlegame: pinned king side",
        "category": "middlegame",
        "fen": "r2q1rk1/ppp2ppp/2n1bn2/3pp3/3PP3/2PB1N1P/PP3PP1/RNBQR1K1 w - - 0 9",
    },
    {
        "name": "Middlegame: isolated queen pawn",
        "category": "middlegame",
        "fen": "r2q1rk1/pp3ppp/2n1bn2/2bp4/3N4/2PB1N2/PP3PPP/R1BQ1RK1 w - - 2 10",
    },
    {
        "name": "Middlegame: rook pressure",
        "category": "middlegame",
        "fen": "2r2rk1/pp2qppp/2n1bn2/3p4/3P4/2PBPN2/PPQ2PPP/R1B2RK1 w - - 0 12",
    },
    {
        "name": "Middlegame: opposite-side castling",
        "category": "middlegame",
        "fen": "r2q1rk1/ppp2ppp/2npbn2/4p3/2B1P3/2NP1N1P/PPP2PP1/R1BQ1RK1 b - - 4 8",
    },
    {
        "name": "Tactical: back rank pressure",
        "category": "tactical",
        "fen": "6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
    },
    {
        "name": "Tactical: queen and rook attack",
        "category": "tactical",
        "fen": "r3r1k1/pp3ppp/2p2n2/3p4/3P2q1/2N1P1P1/PPQ2PBP/R4RK1 w - - 0 16",
    },
    {
        "name": "Tactical: knight fork available",
        "category": "tactical",
        "fen": "r3k2r/ppp2ppp/2n5/3q4/8/2N2N2/PPPP1PPP/R2QKB1R w KQkq - 0 10",
    },
    {
        "name": "Tactical: hanging queen",
        "category": "tactical",
        "fen": "rnb1kbnr/pppp1ppp/8/4p3/4P1q1/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3",
    },
    {
        "name": "Endgame: king and rook vs king",
        "category": "endgame",
        "fen": "8/8/8/8/8/8/5K2/6Rk w - - 0 1",
    },
    {
        "name": "Endgame: king and pawn race",
        "category": "endgame",
        "fen": "8/4k3/8/3P4/8/8/4K3/8 w - - 0 1",
    },
    {
        "name": "Endgame: rook and pawn",
        "category": "endgame",
        "fen": "8/5k2/8/8/5P2/8/5K2/6R1 w - - 0 1",
    },
    {
        "name": "Endgame: bishop vs knight",
        "category": "endgame",
        "fen": "8/5k2/8/8/8/3B4/5K2/6n1 w - - 0 1",
    },
]


def build_positions():
    positions = []

    for position in BLUNDER_POSITIONS:
        positions.append({
            "name": position["name"],
            "category": "blunder",
            "fen": position["fen"],
            "expected_stockfish_best": position.get("stockfish_best"),
            "known_bad_move": position.get("bad_move"),
        })

    positions.extend(EXTRA_POSITIONS)
    return positions


def get_stockfish():
    if not STOCKFISH_PATH:
        return None

    stockfish_path = Path(STOCKFISH_PATH)

    if not stockfish_path.exists():
        return None

    return chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)


def analyse_stockfish(stockfish, board):
    if stockfish is None:
        return None, None

    info = stockfish.analyse(board, chess.engine.Limit(time=STOCKFISH_TIME_PER_POSITION))
    best_move = info.get("pv", [None])[0]
    score = info["score"].pov(board.turn) if "score" in info else None
    return best_move, str(score) if score is not None else None


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    RESULTS_FILE.write_text("", encoding="utf-8")

    positions = build_positions()
    results = []
    stockfish = get_stockfish()

    try:
        for index, position in enumerate(positions, start=1):
            board = chess.Board(position["fen"])
            engine = ChessEngine()
            garry_move = engine.choose_move(board)
            stockfish_move, stockfish_score = analyse_stockfish(stockfish, board)

            garry_uci = garry_move.uci() if garry_move is not None else None
            stockfish_uci = stockfish_move.uci() if stockfish_move is not None else None

            result = {
                "index": index,
                "name": position["name"],
                "category": position["category"],
                "fen": position["fen"],
                "garry_move": garry_uci,
                "garry_eval": engine.last_eval,
                "depth_reached": engine.last_depth_reached,
                "nodes_searched": engine.nodes_searched,
                "tt_hits": engine.tt_hits,
                "aspiration_researches": engine.aspiration_researches,
                "time_used": engine.last_search_time,
                "stockfish_best": stockfish_uci,
                "stockfish_score": stockfish_score,
                "matches_stockfish": (
                    garry_uci == stockfish_uci
                    if stockfish_uci is not None
                    else None
                ),
            }

            results.append(result)

            with open(RESULTS_FILE, "a", encoding="utf-8") as file:
                file.write(json.dumps(result) + "\n")

    finally:
        if stockfish is not None:
            stockfish.quit()

    positions_tested = len(results)
    average_depth = sum(result["depth_reached"] for result in results) / positions_tested
    average_nodes = sum(result["nodes_searched"] for result in results) / positions_tested
    average_tt_hits = sum(result["tt_hits"] for result in results) / positions_tested
    average_aspiration_researches = (
        sum(result["aspiration_researches"] for result in results) / positions_tested
    )
    average_time = sum(result["time_used"] for result in results) / positions_tested

    stockfish_results = [
        result for result in results
        if result["matches_stockfish"] is not None
    ]
    stockfish_matches = sum(
        1 for result in stockfish_results
        if result["matches_stockfish"]
    )
    disagreements = [
        result for result in stockfish_results
        if not result["matches_stockfish"]
    ]

    print("Position Suite Summary")
    print("----------------------")
    print(f"Positions tested: {positions_tested}")

    if stockfish_results:
        print(f"Stockfish matches: {stockfish_matches}/{len(stockfish_results)}")
    else:
        print("Stockfish matches: unavailable")

    print(f"Average depth: {average_depth:.2f}")
    print(f"Average nodes: {average_nodes:.0f}")
    print(f"Average TT hits: {average_tt_hits:.2f}")
    print(f"Average aspiration re-searches: {average_aspiration_researches:.2f}")
    print(f"Average time per position: {average_time:.2f}s")

    if disagreements:
        print()
        print("Disagreements with Stockfish:")

        for result in disagreements:
            print(
                f"{result['index']}. {result['name']}: "
                f"Garry {result['garry_move']} vs Stockfish {result['stockfish_best']}"
            )


if __name__ == "__main__":
    main()
