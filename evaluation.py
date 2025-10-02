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
        
        # Advanced tactical patterns
        score += self._evaluate_bishop_pair(board)
        score += self._evaluate_rook_activity(board)
        score += self._evaluate_knight_outposts(board)
        score += self._evaluate_piece_coordination(board)
        score += self._evaluate_threats(board)
        
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
    
    def _evaluate_bishop_pair(self, board):
        """Evaluate bishop pair bonus"""
        score = 0
        
        white_bishops = board.pieces(chess.BISHOP, chess.WHITE)
        black_bishops = board.pieces(chess.BISHOP, chess.BLACK)
        
        # Bishop pair bonus (having both light and dark squared bishops)
        if len(white_bishops) >= 2:
            score += 50
        if len(black_bishops) >= 2:
            score -= 50
        
        return score
    
    def _evaluate_rook_activity(self, board):
        """Evaluate rook activity on open and semi-open files"""
        score = 0
        
        # Check each file for pawn presence
        for color in [chess.WHITE, chess.BLACK]:
            rooks = board.pieces(chess.ROOK, color)
            
            for rook_square in rooks:
                rook_file = chess.square_file(rook_square)
                
                # Check if file is open or semi-open
                has_own_pawn = False
                has_enemy_pawn = False
                
                for rank in range(8):
                    square = chess.square(rook_file, rank)
                    piece = board.piece_at(square)
                    if piece and piece.piece_type == chess.PAWN:
                        if piece.color == color:
                            has_own_pawn = True
                        else:
                            has_enemy_pawn = True
                
                # Open file (no pawns)
                if not has_own_pawn and not has_enemy_pawn:
                    bonus = 25
                # Semi-open file (no own pawns)
                elif not has_own_pawn:
                    bonus = 15
                # Rook on 7th rank
                elif chess.square_rank(rook_square) == 6 and color == chess.WHITE:
                    bonus = 20
                elif chess.square_rank(rook_square) == 1 and color == chess.BLACK:
                    bonus = 20
                else:
                    bonus = 0
                
                if color == chess.WHITE:
                    score += bonus
                else:
                    score -= bonus
        
        return score
    
    def _evaluate_knight_outposts(self, board):
        """Evaluate knight outposts (strong squares protected by pawns and not attackable by enemy pawns)"""
        score = 0
        
        outpost_squares_white = [chess.C4, chess.C5, chess.C6, chess.D4, chess.D5, chess.D6,
                                  chess.E4, chess.E5, chess.E6, chess.F4, chess.F5, chess.F6]
        outpost_squares_black = [chess.C3, chess.C4, chess.C5, chess.D3, chess.D4, chess.D5,
                                  chess.E3, chess.E4, chess.E5, chess.F3, chess.F4, chess.F5]
        
        # Check white knights
        white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
        black_pawns = board.pieces(chess.PAWN, chess.BLACK)
        
        for knight_square in white_knights:
            if knight_square in outpost_squares_white:
                knight_file = chess.square_file(knight_square)
                knight_rank = chess.square_rank(knight_square)
                
                # Check if protected by own pawn
                protected = False
                for file_offset in [-1, 1]:
                    pawn_file = knight_file + file_offset
                    if 0 <= pawn_file <= 7 and knight_rank > 0:
                        pawn_square = chess.square(pawn_file, knight_rank - 1)
                        piece = board.piece_at(pawn_square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.WHITE:
                            protected = True
                            break
                
                # Check if enemy pawns can attack this square (currently or after advances)
                # Black pawns attack from one rank forward (higher rank number)
                can_be_attacked = False
                for black_pawn_square in black_pawns:
                    pawn_file = chess.square_file(black_pawn_square)
                    pawn_rank = chess.square_rank(black_pawn_square)
                    
                    if abs(pawn_file - knight_file) == 1:
                        # Black pawn attacks diagonally downward (from higher rank to lower)
                        # Currently attacking: pawn on rank R attacks rank R-1
                        if pawn_rank - 1 == knight_rank:
                            can_be_attacked = True
                            break
                        # Can advance one square and attack
                        elif pawn_rank - 2 == knight_rank:
                            advance_square = chess.square(pawn_file, pawn_rank - 1)
                            if not board.piece_at(advance_square):
                                can_be_attacked = True
                                break
                        # Can double-advance from starting rank (rank 6) and attack
                        elif pawn_rank == 6 and pawn_rank - 3 == knight_rank:
                            square_1 = chess.square(pawn_file, pawn_rank - 1)
                            square_2 = chess.square(pawn_file, pawn_rank - 2)
                            if not board.piece_at(square_1) and not board.piece_at(square_2):
                                can_be_attacked = True
                                break
                
                if protected and not can_be_attacked:
                    score += 30
        
        # Check black knights
        black_knights = board.pieces(chess.KNIGHT, chess.BLACK)
        white_pawns = board.pieces(chess.PAWN, chess.WHITE)
        
        for knight_square in black_knights:
            if knight_square in outpost_squares_black:
                knight_file = chess.square_file(knight_square)
                knight_rank = chess.square_rank(knight_square)
                
                # Check if protected by own pawn
                protected = False
                for file_offset in [-1, 1]:
                    pawn_file = knight_file + file_offset
                    if 0 <= pawn_file <= 7 and knight_rank < 7:
                        pawn_square = chess.square(pawn_file, knight_rank + 1)
                        piece = board.piece_at(pawn_square)
                        if piece and piece.piece_type == chess.PAWN and piece.color == chess.BLACK:
                            protected = True
                            break
                
                # Check if enemy pawns can attack this square (currently or after advances)
                # White pawns attack from one rank backward (lower rank number)
                can_be_attacked = False
                for white_pawn_square in white_pawns:
                    pawn_file = chess.square_file(white_pawn_square)
                    pawn_rank = chess.square_rank(white_pawn_square)
                    
                    if abs(pawn_file - knight_file) == 1:
                        # White pawn attacks diagonally upward (from lower rank to higher)
                        # Currently attacking: pawn on rank R attacks rank R+1
                        if pawn_rank + 1 == knight_rank:
                            can_be_attacked = True
                            break
                        # Can advance one square and attack
                        elif pawn_rank + 2 == knight_rank:
                            advance_square = chess.square(pawn_file, pawn_rank + 1)
                            if not board.piece_at(advance_square):
                                can_be_attacked = True
                                break
                        # Can double-advance from starting rank (rank 1) and attack
                        elif pawn_rank == 1 and pawn_rank + 3 == knight_rank:
                            square_1 = chess.square(pawn_file, pawn_rank + 1)
                            square_2 = chess.square(pawn_file, pawn_rank + 2)
                            if not board.piece_at(square_1) and not board.piece_at(square_2):
                                can_be_attacked = True
                                break
                
                if protected and not can_be_attacked:
                    score -= 30
        
        return score
    
    def _evaluate_piece_coordination(self, board):
        """Evaluate piece coordination patterns"""
        score = 0
        
        # Rooks on the same rank or file (battery) with clear line
        for color in [chess.WHITE, chess.BLACK]:
            rooks = list(board.pieces(chess.ROOK, color))
            if len(rooks) == 2:
                r1_file = chess.square_file(rooks[0])
                r1_rank = chess.square_rank(rooks[0])
                r2_file = chess.square_file(rooks[1])
                r2_rank = chess.square_rank(rooks[1])
                
                # Check if same file or rank with clear line
                clear_line = False
                if r1_file == r2_file:
                    # Check vertical line
                    min_rank = min(r1_rank, r2_rank)
                    max_rank = max(r1_rank, r2_rank)
                    clear_line = True
                    for rank in range(min_rank + 1, max_rank):
                        square = chess.square(r1_file, rank)
                        if board.piece_at(square):
                            clear_line = False
                            break
                elif r1_rank == r2_rank:
                    # Check horizontal line
                    min_file = min(r1_file, r2_file)
                    max_file = max(r1_file, r2_file)
                    clear_line = True
                    for file in range(min_file + 1, max_file):
                        square = chess.square(file, r1_rank)
                        if board.piece_at(square):
                            clear_line = False
                            break
                
                if clear_line:
                    bonus = 15
                    if color == chess.WHITE:
                        score += bonus
                    else:
                        score -= bonus
        
        # Bishops on long diagonals
        for color in [chess.WHITE, chess.BLACK]:
            bishops = board.pieces(chess.BISHOP, color)
            for bishop_square in bishops:
                file = chess.square_file(bishop_square)
                rank = chess.square_rank(bishop_square)
                
                # Check if on long diagonal (a1-h8 or a8-h1)
                if file == rank or file + rank == 7:
                    bonus = 10
                    if color == chess.WHITE:
                        score += bonus
                    else:
                        score -= bonus
        
        return score
    
    def _evaluate_threats(self, board):
        """Evaluate threats and hanging pieces"""
        score = 0
        
        # Check for attacked pieces
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Count attackers and defenders
                attackers = board.attackers(not piece.color, square)
                defenders = board.attackers(piece.color, square)
                
                num_attackers = len(list(attackers))
                num_defenders = len(list(defenders))
                
                # Piece is hanging (attacked and not defended)
                if num_attackers > 0 and num_defenders == 0:
                    penalty = self.piece_values.get(piece.piece_type, 0) // 2
                    if piece.color == chess.WHITE:
                        score -= penalty
                    else:
                        score += penalty
                
                # Piece is under attack (more attackers than defenders)
                elif num_attackers > num_defenders:
                    penalty = self.piece_values.get(piece.piece_type, 0) // 4
                    if piece.color == chess.WHITE:
                        score -= penalty
                    else:
                        score += penalty
        
        return score
