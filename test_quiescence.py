import math
import time
import unittest

import chess

from garry_botsparov import ChessEngine


class RecordingEngine(ChessEngine):
    def __init__(self):
        super().__init__(max_depth=1, time_limit=10.0)
        self.search_start_time = time.time()
        self.check_evasions_seen = None

    def order_moves(self, board, moves, tt_move=None):
        moves = list(moves)

        if board.is_check() and self.check_evasions_seen is None:
            self.check_evasions_seen = moves

        return moves

    def evaluate(self, board):
        return 0


class QuiescenceSearchTests(unittest.TestCase):
    def test_searches_all_legal_evasions_when_in_check(self):
        board = chess.Board("4r3/8/8/8/8/8/8/4K3 w - - 0 1")
        engine = RecordingEngine()

        legal_evasions = list(board.legal_moves)

        self.assertTrue(board.is_check())
        self.assertGreater(len(legal_evasions), 0)
        self.assertTrue(
            all(
                not board.is_capture(move) and move.promotion is None
                for move in legal_evasions
            )
        )

        engine.quiescence_search(board, -math.inf, math.inf, depth=2)

        self.assertEqual(set(engine.check_evasions_seen), set(legal_evasions))

    def test_searches_evasions_at_depth_zero_when_in_check(self):
        board = chess.Board("4r3/8/8/8/8/8/8/4K3 w - - 0 1")
        engine = RecordingEngine()

        legal_evasions = list(board.legal_moves)

        self.assertTrue(board.is_check())

        engine.quiescence_search(board, -math.inf, math.inf, depth=0)

        self.assertEqual(set(engine.check_evasions_seen), set(legal_evasions))


if __name__ == "__main__":
    unittest.main()
