import chess
import chess.engine

from garry_botsparov import ChessEngine


STOCKFISH_PATH = r"C:\Users\Tom Greenwood\Desktop\Coding Projects\Chess Bot\stockfish\stockfish-windows-x86-64-avx2.exe"

TEST_POSITIONS = [
    {
        "name": "Old report: Game 40 ply 71",
        "fen": "r1b3kr/pppp2qB/4p3/4P3/3P1RQ1/2n4P/6P1/7K b - - 0 36",
        "bad_move": "g8h7",
        "stockfish_best": "h8h7",
    },
    {
        "name": "Old report: Game 21 ply 50",
        "fen": "r4rk1/3q1ppp/2n5/1P6/8/1p1PN3/1PK1P1P1/R1BQ1B1R w - - 0 26",
        "bad_move": "c2b1",
        "stockfish_best": "c2d2",
    },
    {
        "name": "Old report: Game 16 ply 143",
        "fen": "Q5k1/p1r2p1p/1p2bK2/2p5/3p2P1/8/8/8 b - - 58 72",
        "bad_move": "e6c8",
        "stockfish_best": "c7c8",
    },
    {
        "name": "Old report: Game 40 ply 73",
        "fen": "r1b4r/pppp2qk/4p3/4P3/3P1R1Q/2n4P/6P1/7K b - - 1 37",
        "bad_move": "g7h6",
        "stockfish_best": "h7g6",
    },
    {
        "name": "Old report: Game 21 ply 36",
        "fen": "rnb1k2r/2q2ppp/8/pp6/N7/1K1Pp3/PPP1P1P1/R1BQ1B1R w kq - 0 19",
        "bad_move": "a4c3",
        "stockfish_best": "c2c3",
    },
    {
        "name": "New report: Game 37 ply 78",
        "fen": "5k1r/3qp3/1b3p2/8/4PP2/2P4r/PP1PQ1KP/R1B4R w - - 5 40",
        "bad_move": "a1b1",
        "stockfish_best": "g2f1",
    },
    {
        "name": "New report: Game 16 ply 49",
        "fen": "r1b1qk2/ppppp2B/8/7p/2P4Q/8/PPPK4/R5b1 b - - 2 25",
        "bad_move": "g1b6",
        "stockfish_best": "e8f7",
    },
    {
        "name": "New report: Game 10 ply 71",
        "fen": "3r3r/p1p1R2p/6p1/k2Pp3/4Pp2/1R1B4/1PK4P/6b1 b - - 9 36",
        "bad_move": "g1h2",
        "stockfish_best": "d8b8",
    },
    {
        "name": "New report: Game 8 ply 173",
        "fen": "1k6/p2p2pp/Bp6/3N4/4P3/2R5/6q1/2K5 b - - 67 87",
        "bad_move": "g2h1",
        "stockfish_best": "g2g1",
    },
    {
        "name": "New report: Game 16 ply 41",
        "fen": "r1bq1k1r/ppppp2p/8/5pN1/2P4Q/4b2B/PPP5/R3K1R1 b - - 3 21",
        "bad_move": "e3g1",
        "stockfish_best": "d7d5",
    },
]


def analyse_stockfish(stockfish, board):
    info = stockfish.analyse(board, chess.engine.Limit(time=0.5))
    best_move = info["pv"][0]
    score = info["score"].pov(board.turn)
    return best_move, score


def main():
    blunders_repeated = 0
    stockfish_matches = 0
    different_moves = 0

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as stockfish:
        for test in TEST_POSITIONS:
            board = chess.Board(test["fen"])
            engine = ChessEngine(max_depth=10, time_limit=2.0)

            garry_move = engine.choose_move(board)
            stockfish_move, stockfish_score = analyse_stockfish(stockfish, board)

            garry_uci = garry_move.uci() if garry_move is not None else None

            print()
            print(test["name"])
            print("-" * len(test["name"]))
            print(f"FEN: {test['fen']}")
            print(f"Garry move: {garry_move}")
            print(f"Known bad move: {test['bad_move']}")
            print(f"Report Stockfish best: {test['stockfish_best']}")
            print(f"Current Stockfish best: {stockfish_move}")
            print(f"Stockfish eval: {stockfish_score}")
            print(f"Garry depth: {engine.last_depth_reached}")
            print(f"Garry nodes: {engine.nodes_searched}")
            print(f"Garry eval: {engine.last_eval:.2f}")

            if garry_uci == test["bad_move"]:
                blunders_repeated += 1
                print("Result: STILL CHOOSES THE BLUNDER")
            elif garry_uci == test["stockfish_best"]:
                stockfish_matches += 1
                print("Result: CHOSE REPORT BEST MOVE")
            else:
                different_moves += 1
                print("Result: different move")

    print()
    print("Summary")
    print("-------")
    print(f"Positions tested: {len(TEST_POSITIONS)}")
    print(f"Repeated known blunders: {blunders_repeated}")
    print(f"Matched report Stockfish best: {stockfish_matches}")
    print(f"Different non-blunder moves: {different_moves}")


if __name__ == "__main__":
    main()