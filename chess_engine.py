import chess
from evaluation import PositionEvaluator
from opening_book import OpeningBook
import time

class ChessAI:
    """
    Advanced Chess AI engine using minimax with alpha-beta pruning, iterative deepening,
    quiescence search, move ordering heuristics, and opening book
    """
    
    def __init__(self):
        self.evaluator = PositionEvaluator()
        self.opening_book = OpeningBook()
        self.transposition_table = {}
        self.killer_moves = [[None, None] for _ in range(100)]
        self.history_heuristic = {}
        self.nodes_searched = 0
        self.max_tt_size = 1000000
        print(f"Opening book loaded with {self.opening_book.get_book_size()} positions")
    
    def get_best_move(self, board, max_depth=3, max_time=30.0):
        """
        Get the best move using opening book or iterative deepening search
        
        Args:
            board: chess.Board object
            max_depth: Maximum search depth
            max_time: Maximum time in seconds
            
        Returns:
            chess.Move: The best move found
        """
        # Check opening book first
        book_move = self.opening_book.get_book_move(board)
        if book_move:
            print(f"Opening book move: {book_move}")
            return book_move
        
        self.nodes_searched = 0
        start_time = time.time()
        
        # Ensure we always have a legal move as fallback
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = legal_moves[0]
        best_score = float('-inf') if board.turn == chess.WHITE else float('inf')
        prev_score = None
        
        # Iterative deepening: search progressively deeper
        for current_depth in range(1, max_depth + 1):
            if time.time() - start_time > max_time * 0.9:
                break
            
            depth_best_move, depth_best_score = self._search_depth(
                board, current_depth, start_time, max_time, prev_score
            )
            
            if depth_best_move:
                best_move = depth_best_move
                best_score = depth_best_score
                prev_score = depth_best_score  # Use for next iteration's aspiration window
                print(f"Depth {current_depth}: {best_move} (score: {best_score/100:.2f})")
            
            # Stop if we found a winning move
            if abs(best_score) > 9000:
                break
        
        elapsed = time.time() - start_time
        nps = int(self.nodes_searched / elapsed) if elapsed > 0 else 0
        print(f"AI searched {self.nodes_searched} nodes in {elapsed:.2f}s ({nps} nps)")
        print(f"Best move: {best_move} (score: {best_score/100:.2f})")
        
        return best_move
    
    def _search_depth(self, board, depth, start_time, max_time, prev_score=None):
        """
        Search to a specific depth with aspiration windows
        
        Args:
            board: chess.Board object
            depth: Search depth
            start_time: Start time for time management
            max_time: Maximum allowed time
            prev_score: Previous iteration's score for aspiration window
            
        Returns:
            tuple: (best_move, best_score)
        """
        # Use aspiration windows if we have a previous score
        if prev_score is not None and depth > 2:
            aspiration_window = 50  # Half a pawn
            alpha = prev_score - aspiration_window
            beta = prev_score + aspiration_window
            
            # Try narrow window first
            best_move, best_score = self._search_with_window(
                board, depth, alpha, beta, start_time, max_time
            )
            
            # If we failed low, re-search with full lower bound
            if best_score <= alpha:
                alpha = float('-inf')
                best_move, best_score = self._search_with_window(
                    board, depth, alpha, beta, start_time, max_time
                )
            
            # If we failed high, re-search with full upper bound
            if best_score >= beta:
                beta = float('inf')
                best_move, best_score = self._search_with_window(
                    board, depth, alpha, beta, start_time, max_time
                )
            
            return best_move, best_score
        else:
            # Full window for first iterations
            return self._search_with_window(
                board, depth, float('-inf'), float('inf'), start_time, max_time
            )
    
    def _search_with_window(self, board, depth, alpha, beta, start_time, max_time):
        """
        Search with a specific alpha-beta window
        
        Args:
            board: chess.Board object
            depth: Search depth
            alpha: Lower bound
            beta: Upper bound
            start_time: Start time for time management
            max_time: Maximum allowed time
            
        Returns:
            tuple: (best_move, best_score)
        """
        best_move = None
        
        legal_moves = list(board.legal_moves)
        legal_moves = self.order_moves(board, legal_moves, 0)
        
        is_maximizing = board.turn == chess.WHITE
        best_score = float('-inf') if is_maximizing else float('inf')
        
        for i, move in enumerate(legal_moves):
            if time.time() - start_time > max_time:
                break
            
            board.push(move)
            
            # Principal Variation Search: full window for first move, null window for rest
            if i == 0:
                # Search first move with full window
                score = self.alpha_beta(
                    board, depth - 1, alpha, beta, 
                    not is_maximizing, 1, start_time, max_time
                )
            else:
                # Search with null window (zero-width window)
                if is_maximizing:
                    score = self.alpha_beta(
                        board, depth - 1, alpha, alpha + 1,
                        not is_maximizing, 1, start_time, max_time
                    )
                    # If it beats the null window (score > alpha), re-search with full window
                    if score > alpha and score < beta:
                        score = self.alpha_beta(
                            board, depth - 1, score, beta,
                            not is_maximizing, 1, start_time, max_time
                        )
                else:
                    score = self.alpha_beta(
                        board, depth - 1, beta - 1, beta,
                        not is_maximizing, 1, start_time, max_time
                    )
                    # If it beats the null window (score < beta), re-search with full window
                    if score < beta and score > alpha:
                        score = self.alpha_beta(
                            board, depth - 1, alpha, score,
                            not is_maximizing, 1, start_time, max_time
                        )
            
            board.pop()
            
            # Update best move
            if is_maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)
            
            if beta <= alpha:
                break
        
        return best_move, best_score
    
    def alpha_beta(self, board, depth, alpha, beta, maximizing, ply, start_time, max_time):
        """
        Alpha-beta search with quiescence search
        
        Args:
            board: chess.Board object
            depth: Remaining search depth
            alpha: Alpha value
            beta: Beta value
            maximizing: True if maximizing player
            ply: Current ply from root
            start_time: Start time for time management
            max_time: Maximum allowed time
            
        Returns:
            int: Position evaluation score
        """
        self.nodes_searched += 1
        
        # Time check
        if self.nodes_searched % 1000 == 0:
            if time.time() - start_time > max_time:
                return 0
        
        # Check for draw by repetition or fifty-move rule
        if board.is_repetition(2) or board.halfmove_clock >= 100:
            return 0
        
        # Transposition table lookup
        board_hash = hash(board.fen())
        tt_entry = self.transposition_table.get(board_hash)
        
        if tt_entry and tt_entry['depth'] >= depth:
            tt_flag = tt_entry['flag']
            tt_score = tt_entry['score']
            
            if tt_flag == 'exact':
                return tt_score
            elif tt_flag == 'lower' and tt_score > alpha:
                alpha = tt_score
            elif tt_flag == 'upper' and tt_score < beta:
                beta = tt_score
            
            if alpha >= beta:
                return tt_score
        
        # Terminal node or depth limit - use quiescence search
        if depth <= 0:
            return self.quiescence_search(board, alpha, beta, maximizing, 4)
        
        if board.is_game_over():
            return self.evaluate_terminal_position(board)
        
        # Get and order moves
        legal_moves = list(board.legal_moves)
        legal_moves = self.order_moves(board, legal_moves, ply)
        
        # Save original alpha/beta for transposition table flag determination
        original_alpha = alpha
        original_beta = beta
        
        best_score = float('-inf') if maximizing else float('inf')
        best_move = None
        
        for move in legal_moves:
            board.push(move)
            
            score = self.alpha_beta(
                board, depth - 1, alpha, beta, 
                not maximizing, ply + 1, start_time, max_time
            )
            
            board.pop()
            
            if maximizing:
                if score > best_score:
                    best_score = score
                    best_move = move
                alpha = max(alpha, score)
            else:
                if score < best_score:
                    best_score = score
                    best_move = move
                beta = min(beta, score)
            
            if beta <= alpha:
                # Update killer moves and history
                if not board.is_capture(move):
                    self.update_killers(move, ply)
                    self.update_history(move, depth)
                break
        
        # Store in transposition table with correct flag
        if len(self.transposition_table) < self.max_tt_size:
            # Determine flag based on ORIGINAL alpha/beta window
            flag = 'exact'
            if best_score <= original_alpha:
                flag = 'upper'
            elif best_score >= original_beta:
                flag = 'lower'
            
            self.transposition_table[board_hash] = {
                'score': best_score,
                'depth': depth,
                'flag': flag,
                'move': best_move
            }
        
        return best_score
    
    def quiescence_search(self, board, alpha, beta, maximizing, depth):
        """
        Quiescence search to avoid horizon effect
        Only searches tactical moves (captures, checks)
        
        Args:
            board: chess.Board object
            alpha: Alpha value
            beta: Beta value
            maximizing: True if maximizing player
            depth: Remaining quiescence depth
            
        Returns:
            int: Position evaluation score
        """
        self.nodes_searched += 1
        
        # Stand pat - evaluate current position
        stand_pat = self.evaluator.evaluate_position(board)
        
        if depth == 0:
            return stand_pat
        
        if board.is_game_over():
            return self.evaluate_terminal_position(board)
        
        # Delta pruning - if we're too far behind even with a queen capture
        if maximizing:
            if stand_pat >= beta:
                return beta
            if stand_pat + 900 < alpha:
                return alpha
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            if stand_pat - 900 > beta:
                return beta
            beta = min(beta, stand_pat)
        
        # Only search tactical moves
        tactical_moves = []
        for move in board.legal_moves:
            if board.is_capture(move) or board.gives_check(move):
                tactical_moves.append(move)
        
        tactical_moves = self.order_moves(board, tactical_moves, 0)
        
        for move in tactical_moves:
            board.push(move)
            score = self.quiescence_search(board, alpha, beta, not maximizing, depth - 1)
            board.pop()
            
            if maximizing:
                alpha = max(alpha, score)
                if alpha >= beta:
                    return beta
            else:
                beta = min(beta, score)
                if beta <= alpha:
                    return alpha
        
        return alpha if maximizing else beta
    
    def order_moves(self, board, moves, ply):
        """
        Advanced move ordering for better alpha-beta pruning
        
        Args:
            board: chess.Board object
            moves: List of legal moves
            ply: Current ply from root
            
        Returns:
            list: Ordered list of moves
        """
        def move_priority(move):
            priority = 0
            
            # Check transposition table for best move
            board_hash = hash(board.fen())
            tt_entry = self.transposition_table.get(board_hash)
            if tt_entry and tt_entry.get('move') == move:
                return -1000000
            
            # MVV-LVA for captures
            if board.is_capture(move):
                captured_piece = board.piece_at(move.to_square)
                moving_piece = board.piece_at(move.from_square)
                if captured_piece and moving_piece:
                    priority += self.evaluator.piece_values.get(captured_piece.piece_type, 0) * 10
                    priority -= self.evaluator.piece_values.get(moving_piece.piece_type, 0)
            
            # Killer moves
            if ply < len(self.killer_moves):
                if move == self.killer_moves[ply][0]:
                    priority += 9000
                elif move == self.killer_moves[ply][1]:
                    priority += 8000
            
            # History heuristic
            move_key = (move.from_square, move.to_square)
            priority += self.history_heuristic.get(move_key, 0)
            
            # Checks
            board.push(move)
            if board.is_check():
                priority += 5000
            board.pop()
            
            # Promotions
            if move.promotion:
                priority += 8500
            
            return -priority
        
        return sorted(moves, key=move_priority)
    
    def update_killers(self, move, ply):
        """Update killer moves heuristic"""
        if ply < len(self.killer_moves):
            if self.killer_moves[ply][0] != move:
                self.killer_moves[ply][1] = self.killer_moves[ply][0]
                self.killer_moves[ply][0] = move
    
    def update_history(self, move, depth):
        """Update history heuristic"""
        move_key = (move.from_square, move.to_square)
        self.history_heuristic[move_key] = self.history_heuristic.get(move_key, 0) + depth * depth
    
    def evaluate_terminal_position(self, board):
        """
        Evaluate terminal positions (checkmate, stalemate)
        
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
