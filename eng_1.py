import chess
import math
import time


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


PAWN_TABLE = [
      0,   0,   0,   0,   0,   0,   0,   0,
     50,  50,  50,  50,  50,  50,  50,  50,
     10,  10,  20,  30,  30,  20,  10,  10,
      5,   5,  10,  25,  25,  10,   5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      5,  10,  10, -20, -20,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_TABLE = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

BISHOP_TABLE = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

ROOK_TABLE = [
      0,   0,   5,  10,  10,   5,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   5,   5,   0,   0,   0,
]

QUEEN_TABLE = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -10,   5,   5,   5,   5,   5,   0, -10,
      0,   0,   5,   5,   5,   5,   0,  -5,
     -5,   0,   5,   5,   5,   5,   0,  -5,
    -10,   0,   5,   5,   5,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]

KING_TABLE = [
     20,  30,  10,   0,   0,  10,  30,  20,
     20,  20,   0,   0,   0,   0,  20,  20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
]


PIECE_SQUARE_TABLES = {
    chess.PAWN: PAWN_TABLE,
    chess.KNIGHT: KNIGHT_TABLE,
    chess.BISHOP: BISHOP_TABLE,
    chess.ROOK: ROOK_TABLE,
    chess.QUEEN: QUEEN_TABLE,
    chess.KING: KING_TABLE,
}


class ChessEngine:
    def __init__(self, depth=3):
        self.depth = depth
        self.nodes_searched = 0

    def choose_move(self, board):
        self.nodes_searched = 0

        best_move = None
        best_score = -math.inf

        alpha = -math.inf
        beta = math.inf

        moves = self.order_moves(board, list(board.legal_moves))

        start_time = time.time()

        for move in moves:
            board.push(move)

            score = -self.negamax(board, self.depth - 1, -beta, -alpha)

            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, best_score)

        elapsed = time.time() - start_time

        print()
        print(f"engine searched {self.nodes_searched} nodes in {elapsed:.2f} s")
        print(f"engine evaluation: {best_score / 100:.2f} pawns")
        print(f"engine move: {best_move}")
        print()

        return best_move

    def negamax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if board.is_checkmate():
            return -100000 - depth

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        if depth == 0:
            return self.evaluate(board)

        best_score = -math.inf

        moves = self.order_moves(board, list(board.legal_moves))

        for move in moves:
            board.push(move)

            score = -self.negamax(board, depth - 1, -beta, -alpha)

            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if alpha >= beta:
                break

        return best_score

    def evaluate(self, board):
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -100000
            return 100000

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0

        for square, piece in board.piece_map().items():
            value = PIECE_VALUES[piece.piece_type]
            positional_value = self.get_piece_square_value(piece, square)

            if piece.color == chess.WHITE:
                score += value + positional_value
            else:
                score -= value + positional_value

        score += self.evaluate_mobility(board)

        if board.turn == chess.WHITE:
            return score

        return -score

    def get_piece_square_value(self, piece, square):
        table = PIECE_SQUARE_TABLES[piece.piece_type]

        if piece.color == chess.WHITE:
            return table[square]

        mirrored_square = chess.square_mirror(square)
        return table[mirrored_square]

    def evaluate_mobility(self, board):
        current_turn = board.turn

        board.turn = chess.WHITE
        white_mobility = len(list(board.legal_moves))

        board.turn = chess.BLACK
        black_mobility = len(list(board.legal_moves))

        board.turn = current_turn

        return 2 * (white_mobility - black_mobility)

    def order_moves(self, board, moves):
        def move_score(move):
            score = 0

            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)

                if victim is not None and attacker is not None:
                    score += 10 * PIECE_VALUES[victim.piece_type]
                    score -= PIECE_VALUES[attacker.piece_type]

            if move.promotion is not None:
                score += PIECE_VALUES[move.promotion]

            board.push(move)

            if board.is_check():
                score += 50

            board.pop()

            return score

        return sorted(moves, key=move_score, reverse=True)


def print_board(board):
    print()
    print(board)
    print()
    print(f"FEN: {board.fen()}")
    print()


def get_player_move(board):
    while True:
        move_text = input("your move: ").strip()

        if move_text.lower() in {"quit", "exit"}:
            return None

        try:
            move = chess.Move.from_uci(move_text)
        except ValueError:
            print("invalid format. use UCI notation, e.g. e2e4, g1f3, e7e8q.")
            continue

        if move not in board.legal_moves:
            print("illegal move. try again.")
            continue

        return move


def choose_player_colour():
    while True:
        choice = input("play as white or black? [w/b]: ").strip().lower()

        if choice in {"w", "white"}:
            return chess.WHITE

        if choice in {"b", "black"}:
            return chess.BLACK

        print("please enter w or b.")


def choose_depth():
    while True:
        choice = input("engine search depth? recommended 2-4: ").strip()

        try:
            depth = int(choice)
        except ValueError:
            print("please enter a whole number.")
            continue

        if depth < 1:
            print("depth must be at least 1.")
            continue

        return depth


def main():
    board = chess.Board()

    player_colour = choose_player_colour()
    depth = choose_depth()

    engine = ChessEngine(depth=depth)

    print()
    print("enter moves in UCI format.")
    print("examples: e2e4, g1f3, e7e8q")
    print("type quit to stop.")
    print()

    while not board.is_game_over():
        print_board(board)

        if board.turn == player_colour:
            move = get_player_move(board)

            if move is None:
                print("game stopped.")
                return

            board.push(move)

        else:
            engine_move = engine.choose_move(board)
            board.push(engine_move)

    print_board(board)

    print("game over")
    print(f"result: {board.result()}")

    outcome = board.outcome()

    if outcome is not None:
        print(f"termination: {outcome.termination}")

        if outcome.winner == chess.WHITE:
            print("winner: white")
        elif outcome.winner == chess.BLACK:
            print("winner: black")
        else:
            print("winner: draw")


if __name__ == "__main__":
    main()