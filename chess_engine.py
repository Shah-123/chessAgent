import chess
import chess.engine
from evaluation import PositionEvaluator
import time

class ChessAI:
    """
    Chess AI engine using minimax algorithm with alpha-beta pruning
    """
    
    def __init__(self):
        self.evaluator = PositionEvaluator()
        self.transposition_table = {}
        self.nodes_searched = 0
    
    def get_best_move(self, board, depth=3):
        """
        Get the best move for the current position using minimax with alpha-beta pruning
        
        Args:
            board: chess.Board object
            depth: Search depth in ply
            
        Returns:
            chess.Move: The best move found
        """
        self.nodes_searched = 0
        self.transposition_table.clear()
        
        start_time = time.time()
        
        best_move = None
        best_score = float('-inf') if board.turn == chess.WHITE else float('inf')
        
        legal_moves = list(board.legal_moves)
        # Order moves for better alpha-beta pruning
        legal_moves = self.order_moves(board, legal_moves)
        
        alpha = float('-inf')
        beta = float('inf')
        
        for move in legal_moves:
            board.push(move)
            
            if board.turn == chess.WHITE:  # After move, it's white's turn, so we were maximizing (black moved)
                score = self.minimax(board, depth - 1, alpha, beta, True)
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
            else:  # After move, it's black's turn, so we were minimizing (white moved)
                score = self.minimax(board, depth - 1, alpha, beta, False)
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)
            
            board.pop()
            
            if beta <= alpha:
                break
        
        end_time = time.time()
        print(f"AI searched {self.nodes_searched} nodes in {end_time - start_time:.2f} seconds")
        print(f"Best move: {best_move} with score: {best_score}")
        
        return best_move
    
    def minimax(self, board, depth, alpha, beta, maximizing_player):
        """
        Minimax algorithm with alpha-beta pruning
        
        Args:
            board: chess.Board object
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: True if maximizing, False if minimizing
            
        Returns:
            int: Position evaluation score
        """
        self.nodes_searched += 1
        
        # Check transposition table
        board_hash = hash(board.fen())
        if board_hash in self.transposition_table:
            tt_entry = self.transposition_table[board_hash]
            if tt_entry['depth'] >= depth:
                return tt_entry['score']
        
        # Terminal node evaluation
        if depth == 0 or board.is_game_over():
            score = self.evaluate_terminal_position(board)
            self.transposition_table[board_hash] = {'score': score, 'depth': depth}
            return score
        
        legal_moves = list(board.legal_moves)
        legal_moves = self.order_moves(board, legal_moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            self.transposition_table[board_hash] = {'score': max_eval, 'depth': depth}
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha-beta pruning
            
            self.transposition_table[board_hash] = {'score': min_eval, 'depth': depth}
            return min_eval
    
    def evaluate_terminal_position(self, board):
        """
        Evaluate terminal positions (game over or leaf nodes)
        
        Args:
            board: chess.Board object
            
        Returns:
            int: Position evaluation score
        """
        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000
        elif board.is_stalemate() or board.is_insufficient_material():
            return 0
        else:
            return self.evaluator.evaluate_position(board)
    
    def order_moves(self, board, moves):
        """
        Order moves for better alpha-beta pruning efficiency
        
        Args:
            board: chess.Board object
            moves: List of legal moves
            
        Returns:
            list: Ordered list of moves
        """
        def move_priority(move):
            priority = 0
            
            # Prioritize captures
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                moving_piece = board.piece_at(move.from_square)
                if captured_piece and moving_piece:
                    # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
                    priority += self.evaluator.piece_values.get(captured_piece.piece_type, 0) * 10
                    priority -= self.evaluator.piece_values.get(moving_piece.piece_type, 0)
            
            # Prioritize checks
            board.push(move)
            if board.is_check():
                priority += 50
            board.pop()
            
            # Prioritize central moves
            to_file = chess.square_file(move.to_square)
            to_rank = chess.square_rank(move.to_square)
            if 2 <= to_file <= 5 and 2 <= to_rank <= 5:
                priority += 10
            
            return -priority  # Negative for descending order
        
        return sorted(moves, key=move_priority)
