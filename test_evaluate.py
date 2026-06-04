import unittest

import chess

import garry_botsparov as gb
from garry_botsparov import ChessEngine


def old_evaluate(engine, board):
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -100000
        return 100000

    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    score = 0

    for square, piece in board.piece_map().items():
        value = gb.PIECE_VALUES[piece.piece_type]
        positional_value = engine.get_piece_square_value(piece, square)

        if piece.color == chess.WHITE:
            score += value + positional_value
        else:
            score -= value + positional_value

    if gb.USE_KING_SAFETY:
        king_danger = engine.evaluate_king_danger(board)
        score += int(engine.king_safety_phase(board) * king_danger)

    if board.turn == chess.WHITE:
        return score

    return -score


class EvaluateTests(unittest.TestCase):
    def test_optimized_evaluate_matches_old_formula(self):
        fens = [
            chess.STARTING_FEN,
            "r1bq1rk1/ppp2ppp/2np1n2/4p3/2B1P3/2NP1N2/PPP2PPP/R1BQ1RK1 w - - 2 7",
            "4r3/8/8/8/8/8/8/4K3 w - - 0 1",
            "r1b1qk2/ppppp2B/8/7p/2P4Q/8/PPPK4/R5b1 b - - 2 25",
            "5k1r/3qp3/1b3p2/8/4PP2/2P4r/PP1PQ1KP/R1B4R w - - 5 40",
        ]

        original_use_king_safety = gb.USE_KING_SAFETY
        engine = ChessEngine()

        try:
            for use_king_safety in (False, True):
                gb.USE_KING_SAFETY = use_king_safety

                for fen in fens:
                    board = chess.Board(fen)

                    with self.subTest(fen=fen, use_king_safety=use_king_safety):
                        self.assertEqual(engine.evaluate(board), old_evaluate(engine, board))
        finally:
            gb.USE_KING_SAFETY = original_use_king_safety


if __name__ == "__main__":
    unittest.main()
