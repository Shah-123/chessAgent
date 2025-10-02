import chess
import numpy as np

class PositionEvaluator:
    """
    Chess position evaluator considering material, piece positioning, and basic tactics
    """
    
    def __init__(self):
        # Piece values in centipawns
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0  # King safety is evaluated separately
        }
        
        # Piece-square tables for positional evaluation
        self.piece_square_tables = self._initialize_piece_square_tables()
    
    def _initialize_piece_square_tables(self):
        """Initialize piece-square tables for positional evaluation"""
        
        # Pawn position values
        pawn_table = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [ 5,  5, 10, 25, 25, 10,  5,  5],
            [ 0,  0,  0, 20, 20,  0,  0,  0],
            [ 5, -5,-10,  0,  0,-10, -5,  5],
            [ 5, 10, 10,-20,-20, 10, 10,  5],
            [ 0,  0,  0,  0,  0,  0,  0,  0]
        ])
        
        # Knight position values
        knight_table = np.array([
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ])
        
        # Bishop position values
        bishop_table = np.array([
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ])
        
        # Rook position values
        rook_table = np.array([
            [ 0,  0,  0,  0,  0,  0,  0,  0],
            [ 5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [ 0,  0,  0,  5,  5,  0,  0,  0]
        ])
        
        # Queen position values
        queen_table = np.array([
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [ -5,  0,  5,  5,  5,  5,  0, -5],
            [  0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ])
        
        # King position values (middlegame)
        king_table_mg = np.array([
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [ 20, 20,  0,  0,  0,  0, 20, 20],
            [ 20, 30, 10,  0,  0, 10, 30, 20]
        ])
        
        # King position values (endgame)
        king_table_eg = np.array([
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-30,  0,  0,  0,  0,-30,-30],
            [-50,-30,-30,-30,-30,-30,-30,-50]
        ])
        
        return {
            chess.PAWN: pawn_table,
            chess.KNIGHT: knight_table,
            chess.BISHOP: bishop_table,
            chess.ROOK: rook_table,
            chess.QUEEN: queen_table,
            chess.KING: king_table_mg,  # Will use endgame table when appropriate
            'king_endgame': king_table_eg
        }
    
    def evaluate_position(self, board):
        """
        Evaluate the current position
        
        Args:
            board: chess.Board object
            
        Returns:
            int: Evaluation score in centipawns (positive = white advantage)
        """
        if board.is_checkmate():
            return -10000 if board.turn == chess.WHITE else 10000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        score = 0
        
        # Material evaluation
        score += self._evaluate_material(board)
        
        # Positional evaluation
        score += self._evaluate_position_tables(board)
        
        # King safety
        score += self._evaluate_king_safety(board)
        
        # Pawn structure
        score += self._evaluate_pawn_structure(board)
        
        # Piece mobility
        score += self._evaluate_mobility(board)
        
        # Center control
        score += self._evaluate_center_control(board)
        
        return score
    
    def _evaluate_material(self, board):
        """Evaluate material balance"""
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        return score
    
    def _evaluate_position_tables(self, board):
        """Evaluate piece positions using piece-square tables"""
        score = 0
        is_endgame = self._is_endgame(board)
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                file_idx = chess.square_file(square)
                rank_idx = chess.square_rank(square)
                
                # For black pieces, flip the rank
                if piece.color == chess.BLACK:
                    rank_idx = 7 - rank_idx
                
                piece_type = piece.piece_type
                if piece_type == chess.KING and is_endgame:
                    table_value = self.piece_square_tables['king_endgame'][rank_idx][file_idx]
                else:
                    table_value = self.piece_square_tables.get(piece_type, np.zeros((8, 8)))[rank_idx][file_idx]
                
                if piece.color == chess.WHITE:
                    score += table_value
                else:
                    score -= table_value
        
        return score
    
    def _evaluate_king_safety(self, board):
        """Evaluate king safety"""
        score = 0
        
        # Find kings
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        if white_king_square is not None:
            score += self._king_safety_score(board, white_king_square, chess.WHITE)
        
        if black_king_square is not None:
            score -= self._king_safety_score(board, black_king_square, chess.BLACK)
        
        return score
    
    def _king_safety_score(self, board, king_square, color):
        """Calculate king safety score for a specific king"""
        safety_score = 0
        
        # Penalty for exposed king
        if not self._is_endgame(board):
            # Check pawn shield
            king_file = chess.square_file(king_square)
            king_rank = chess.square_rank(king_square)
            
            shield_squares = []
            if color == chess.WHITE:
                for file_offset in [-1, 0, 1]:
                    shield_file = king_file + file_offset
                    if 0 <= shield_file <= 7:
                        shield_square = chess.square(shield_file, min(king_rank + 1, 7))
                        shield_squares.append(shield_square)
            else:
                for file_offset in [-1, 0, 1]:
                    shield_file = king_file + file_offset
                    if 0 <= shield_file <= 7:
                        shield_square = chess.square(shield_file, max(king_rank - 1, 0))
                        shield_squares.append(shield_square)
            
            # Check for pawn shield
            for square in shield_squares:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    safety_score += 10
                else:
                    safety_score -= 15  # Penalty for missing pawn
        
        return safety_score
    
    def _evaluate_pawn_structure(self, board):
        """Evaluate pawn structure"""
        score = 0
        
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        # Doubled pawns penalty
        score -= self._count_doubled_pawns(white_pawns) * 10
        score += self._count_doubled_pawns(black_pawns) * 10
        
        # Isolated pawns penalty
        score -= self._count_isolated_pawns(white_pawns) * 15
        score += self._count_isolated_pawns(black_pawns) * 15
        
        # Passed pawns bonus
        score += self._count_passed_pawns(board, chess.WHITE) * 20
        score -= self._count_passed_pawns(board, chess.BLACK) * 20
        
        return score
    
    def _evaluate_mobility(self, board):
        """Evaluate piece mobility"""
        # Store current turn
        current_turn = board.turn
        
        # Count white mobility
        board.turn = chess.WHITE
        white_mobility = board.legal_moves.count()
        
        # Count black mobility
        board.turn = chess.BLACK
        black_mobility = board.legal_moves.count()
        
        # Restore original turn
        board.turn = current_turn
        
        return (white_mobility - black_mobility) * 2
    
    def _evaluate_center_control(self, board):
        """Evaluate control of central squares"""
        center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
        extended_center = [chess.C3, chess.C4, chess.C5, chess.C6,
                          chess.D3, chess.D6, chess.E3, chess.E6,
                          chess.F3, chess.F4, chess.F5, chess.F6]
        
        score = 0
        
        # Central squares
        for square in center_squares:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 20
                else:
                    score -= 20
        
        # Extended center
        for square in extended_center:
            piece = board.piece_at(square)
            if piece:
                if piece.color == chess.WHITE:
                    score += 5
                else:
                    score -= 5
        
        return score
    
    def _is_endgame(self, board):
        """Determine if position is in endgame"""
        piece_count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.piece_type != chess.KING and piece.piece_type != chess.PAWN:
                piece_count += 1
        return piece_count <= 6
    
    def _count_doubled_pawns(self, pawns):
        """Count doubled pawns"""
        files = {}
        for pawn_square in pawns:
            file_idx = chess.square_file(pawn_square)
            files[file_idx] = files.get(file_idx, 0) + 1
        
        doubled = 0
        for file_idx, count in files.items():
            if count > 1:
                doubled += count - 1
        return doubled
    
    def _count_isolated_pawns(self, pawns):
        """Count isolated pawns"""
        files = set()
        for pawn_square in pawns:
            files.add(chess.square_file(pawn_square))
        
        isolated = 0
        for file_idx in files:
            has_neighbor = False
            for neighbor_file in [file_idx - 1, file_idx + 1]:
                if neighbor_file in files:
                    has_neighbor = True
                    break
            if not has_neighbor:
                isolated += 1
        return isolated
    
    def _count_passed_pawns(self, board, color):
        """Count passed pawns"""
        passed = 0
        pawns = board.pieces(chess.PAWN, color)
        opponent_pawns = board.pieces(chess.PAWN, not color)
        
        for pawn_square in pawns:
            pawn_file = chess.square_file(pawn_square)
            pawn_rank = chess.square_rank(pawn_square)
            
            is_passed = True
            for opp_pawn_square in opponent_pawns:
                opp_file = chess.square_file(opp_pawn_square)
                opp_rank = chess.square_rank(opp_pawn_square)
                
                # Check if opponent pawn can stop this pawn
                if abs(opp_file - pawn_file) <= 1:
                    if color == chess.WHITE and opp_rank > pawn_rank:
                        is_passed = False
                        break
                    elif color == chess.BLACK and opp_rank < pawn_rank:
                        is_passed = False
                        break
            
            if is_passed:
                passed += 1
        
        return passed
