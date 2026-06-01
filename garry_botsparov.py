import math
import time

import chess
import pygame

# engine settings
ENGINE_DEPTH = 4
PLAYER_COLOUR = chess.WHITE
QUIESCENCE_DEPTH = 4

# graphics settings
WIDTH = 640
HEIGHT = 720
BOARD_SIZE = 640
SQUARE_SIZE = BOARD_SIZE // 8
INFO_HEIGHT = HEIGHT - BOARD_SIZE
FPS = 60
FLIP_BOARD_FOR_BLACK = False

LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
SELECTED_SQUARE = (246, 246, 105)
LEGAL_MOVE_DOT = (40, 40, 40)
LAST_MOVE = (186, 202, 68)
TEXT_COLOUR = (20, 20, 20)
BACKGROUND = (230, 230, 230)

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
    def __init__(self, depth=ENGINE_DEPTH):
        self.depth = depth
        self.nodes_searched = 0
        self.last_eval = 0.0
        self.last_search_time = 0.0

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

        self.last_search_time = time.time() - start_time
        if board.turn == PLAYER_COLOUR:
            self.last_eval = best_score / 100
        else:
            self.last_eval = -best_score / 100

        return best_move

    def negamax(self, board, depth, alpha, beta):
        self.nodes_searched += 1

        if board.is_checkmate():
            return -100000 - depth

        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        if board.is_repetition(3) or board.can_claim_fifty_moves():
            if self.evaluate(board) > 0:
                return -5000
            return 0

        if depth == 0:
            return self.quiescence_search(board, alpha, beta, QUIESCENCE_DEPTH)

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

    def quiescence_search(self, board, alpha, beta, depth):
        self.nodes_searched += 1

        stand_pat = self.evaluate(board)

        if depth == 0:
            return stand_pat

        if stand_pat >= beta:
            return beta

        if alpha < stand_pat:
            alpha = stand_pat

        capture_moves = [
            move for move in board.legal_moves
            if board.is_capture(move) or move.promotion is not None
        ]

        capture_moves = self.order_moves(board, capture_moves)

        for move in capture_moves:
            board.push(move)

            score = -self.quiescence_search(board, -beta, -alpha, depth - 1)

            board.pop()

            if score >= beta:
                return beta

            if score > alpha:
                alpha = score

        return alpha

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


class ChessGUI:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Tom's Chess Engine")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.board = chess.Board()
        self.engine = ChessEngine(depth=ENGINE_DEPTH)

        self.player_colour = PLAYER_COLOUR
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.status = "Your move. Press U to undo, R to reset, ESC to quit."

        self.piece_font = pygame.font.SysFont("segoeuisymbol", 56)

        if self.board.turn != self.player_colour:
            self.engine_reply()

    def run(self):
        running = True

        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.draw()

        pygame.quit()

    def handle_keydown(self, event):
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            raise SystemExit

        if event.key == pygame.K_r:
            self.reset_game()

        if event.key == pygame.K_u:
            self.undo_move()

    def handle_click(self, pos):
        if self.board.is_game_over():
            return

        if self.board.turn != self.player_colour:
            return

        x, y = pos

        if y >= BOARD_SIZE:
            return

        clicked_square = self.pixel_to_square(x, y)

        if self.selected_square is None:
            self.select_square(clicked_square)
            return

        move = self.make_move_from_selection(self.selected_square, clicked_square)

        if move in self.board.legal_moves:
            self.play_move(move)
            self.selected_square = None
            self.legal_targets = []

            if self.board.is_game_over():
                self.update_status()
            else:
                self.engine_reply()
        else:
            self.select_square(clicked_square)

    def select_square(self, square):
        piece = self.board.piece_at(square)

        if piece is None or piece.color != self.player_colour:
            self.selected_square = None
            self.legal_targets = []
            return

        self.selected_square = square
        self.legal_targets = [
            move.to_square
            for move in self.board.legal_moves
            if move.from_square == square
        ]

    def make_move_from_selection(self, from_square, to_square):
        piece = self.board.piece_at(from_square)

        if piece is None:
            return chess.Move.null()

        promotion = None

        if piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(to_square)

            if target_rank == 0 or target_rank == 7:
                promotion = chess.QUEEN

        return chess.Move(from_square, to_square, promotion=promotion)

    def play_move(self, move):
        self.board.push(move)
        self.last_move = move

    def engine_reply(self):
        self.status = "Engine thinking..."
        self.draw()
        pygame.display.flip()

        move = self.engine.choose_move(self.board)

        if move is not None:
            self.board.push(move)
            self.last_move = move

        self.update_status()

    def update_status(self):
        if self.board.is_checkmate():
            winner = "White" if self.board.turn == chess.BLACK else "Black"
            self.status = f"Checkmate — {winner} wins."
            return

        if self.board.is_stalemate():
            self.status = "Draw by stalemate."
            return

        if self.board.is_insufficient_material():
            self.status = "Draw by insufficient material."
            return

        if self.board.is_repetition(5):
            self.status = "Draw by fivefold repetition."
            return

        if self.board.is_game_over():
            self.status = f"Game over: {self.board.result()}"
            return

        self.status = (
            f"Engine eval: {self.engine.last_eval:.2f} pawns | "
            f"Nodes: {self.engine.nodes_searched} | "
            f"Time: {self.engine.last_search_time:.2f}s"
        )

    def undo_move(self):
        if len(self.board.move_stack) >= 2:
            self.board.pop()
            self.board.pop()
            self.last_move = self.board.peek() if self.board.move_stack else None
            self.selected_square = None
            self.legal_targets = []
            self.status = "Undid last full move."

    def reset_game(self):
        self.board = chess.Board()
        self.selected_square = None
        self.legal_targets = []
        self.last_move = None
        self.status = "New game."

        if self.board.turn != self.player_colour:
            self.engine_reply()
        else:
            self.status = "Your move."

    def draw(self):
        self.screen.fill(BACKGROUND)
        self.draw_board()
        self.draw_pieces()
        self.draw_info_panel()

        pygame.display.flip()

    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                square = self.display_to_square(file, rank)
                colour = LIGHT_SQUARE if (rank + file) % 2 == 0 else DARK_SQUARE

                rect = pygame.Rect(
                    file * SQUARE_SIZE,
                    rank * SQUARE_SIZE,
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                )

                pygame.draw.rect(self.screen, colour, rect)

                if self.last_move is not None:
                    if square in {self.last_move.from_square, self.last_move.to_square}:
                        pygame.draw.rect(self.screen, LAST_MOVE, rect)

                if square == self.selected_square:
                    pygame.draw.rect(self.screen, SELECTED_SQUARE, rect)

        for target in self.legal_targets:
            file, rank = self.square_to_display(target)
            centre = (
                file * SQUARE_SIZE + SQUARE_SIZE // 2,
                rank * SQUARE_SIZE + SQUARE_SIZE // 2,
            )
            pygame.draw.circle(self.screen, LEGAL_MOVE_DOT, centre, 10)

    def draw_pieces(self):
        for square, piece in self.board.piece_map().items():
            file, rank = self.square_to_display(square)
            symbol = self.piece_to_unicode(piece)

            text = self.piece_font.render(symbol, True, TEXT_COLOUR)
            rect = text.get_rect(
                center=(
                    file * SQUARE_SIZE + SQUARE_SIZE // 2,
                    rank * SQUARE_SIZE + SQUARE_SIZE // 2,
                )
            )

            self.screen.blit(text, rect)

    def draw_info_panel(self):
        panel_rect = pygame.Rect(0, BOARD_SIZE, WIDTH, INFO_HEIGHT)
        pygame.draw.rect(self.screen, BACKGROUND, panel_rect)

        turn = "White" if self.board.turn == chess.WHITE else "Black"
        turn_text = self.font.render(f"Turn: {turn}", True, TEXT_COLOUR)
        self.screen.blit(turn_text, (16, BOARD_SIZE + 10))

        status_text = self.small_font.render(self.status, True, TEXT_COLOUR)
        self.screen.blit(status_text, (16, BOARD_SIZE + 42))

    def pixel_to_square(self, x, y):
        file = x // SQUARE_SIZE
        rank = y // SQUARE_SIZE
        return self.display_to_square(file, rank)

    def display_to_square(self, file, display_rank):
        should_flip = self.player_colour == chess.BLACK and FLIP_BOARD_FOR_BLACK

        if not should_flip:
            chess_rank = 7 - display_rank
            return chess.square(file, chess_rank)

        chess_rank = display_rank
        flipped_file = 7 - file
        return chess.square(flipped_file, chess_rank)

    def square_to_display(self, square):
        file = chess.square_file(square)
        chess_rank = chess.square_rank(square)

        should_flip = self.player_colour == chess.BLACK and FLIP_BOARD_FOR_BLACK

        if not should_flip:
            display_rank = 7 - chess_rank
            return file, display_rank

        display_file = 7 - file
        display_rank = chess_rank
        return display_file, display_rank

    def piece_to_unicode(self, piece):
        symbols = {
            chess.PAWN: "♙" if piece.color == chess.WHITE else "♟",
            chess.KNIGHT: "♘" if piece.color == chess.WHITE else "♞",
            chess.BISHOP: "♗" if piece.color == chess.WHITE else "♝",
            chess.ROOK: "♖" if piece.color == chess.WHITE else "♜",
            chess.QUEEN: "♕" if piece.color == chess.WHITE else "♛",
            chess.KING: "♔" if piece.color == chess.WHITE else "♚",
        }

        return symbols[piece.piece_type]


if __name__ == "__main__":
    gui = ChessGUI()
    gui.run()