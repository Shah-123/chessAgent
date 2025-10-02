import chess
import random

class OpeningBook:
    """
    Opening book database for strong early-game play
    Contains common chess openings and their best moves
    """
    
    def __init__(self):
        self.book = self._initialize_opening_book()
    
    def _initialize_opening_book(self):
        """
        Initialize opening book with popular openings and variations
        Maps FEN positions (first 4 fields only) to lists of good moves
        """
        book = {}
        
        # Starting position
        book["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"] = [
            "e2e4", "d2d4", "c2c4", "g1f3"
        ]
        
        # After 1. e4
        book["rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3"] = [
            "e7e5", "c7c5", "e7e6", "c7c6", "d7d5"
        ]
        
        # After 1. e4 e5
        book["rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6"] = [
            "g1f3", "f2f4", "b1c3", "f1c4"
        ]
        
        # After 1. e4 e5 2. Nf3
        book["rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -"] = [
            "b8c6", "g8f6", "d7d6"
        ]
        
        # After 1. e4 e5 2. Nf3 Nc6
        book["r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -"] = [
            "f1b5", "f1c4", "d2d4", "b1c3"
        ]
        
        # Spanish Opening (Ruy Lopez): 1. e4 e5 2. Nf3 Nc6 3. Bb5
        book["r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq -"] = [
            "a7a6", "g8f6", "f7f5", "g7g6"
        ]
        
        # Spanish Opening: 1. e4 e5 2. Nf3 Nc6 3. Bb5 a6
        book["r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq -"] = [
            "b5a4", "b5c6"
        ]
        
        # Italian Game: 1. e4 e5 2. Nf3 Nc6 3. Bc4
        book["r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq -"] = [
            "f8c5", "g8f6", "f8e7"
        ]
        
        # Sicilian Defense: 1. e4 c5
        book["rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6"] = [
            "g1f3", "b1c3", "c2c3"
        ]
        
        # Sicilian: 1. e4 c5 2. Nf3
        book["rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq -"] = [
            "d7d6", "b8c6", "e7e6", "g7g6"
        ]
        
        # Sicilian: 1. e4 c5 2. Nf3 d6
        book["rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq -"] = [
            "d2d4", "f1b5", "c2c3"
        ]
        
        # French Defense: 1. e4 e6
        book["rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"] = [
            "d2d4", "d2d3", "b1c3"
        ]
        
        # French: 1. e4 e6 2. d4
        book["rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3"] = [
            "d7d5", "c7c5"
        ]
        
        # Caro-Kann Defense: 1. e4 c6
        book["rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq -"] = [
            "d2d4", "b1c3", "g1f3"
        ]
        
        # Caro-Kann: 1. e4 c6 2. d4
        book["rnbqkbnr/pp1ppppp/2p5/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq d3"] = [
            "d7d5"
        ]
        
        # After 1. d4
        book["rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3"] = [
            "g8f6", "d7d5", "e7e6", "f7f5"
        ]
        
        # After 1. d4 Nf6
        book["rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR w KQkq -"] = [
            "c2c4", "g1f3", "b1c3"
        ]
        
        # After 1. d4 Nf6 2. c4 (Indian Game)
        book["rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3"] = [
            "e7e6", "g7g6", "c7c5", "e7e5"
        ]
        
        # Queen's Gambit: 1. d4 d5 2. c4
        book["rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq c3"] = [
            "e7e6", "c7c6", "d5c4", "g8f6"
        ]
        
        # Queen's Gambit Accepted: 1. d4 d5 2. c4 dxc4
        book["rnbqkbnr/ppp1pppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq -"] = [
            "g1f3", "e2e3", "e2e4"
        ]
        
        # Queen's Gambit Declined: 1. d4 d5 2. c4 e6
        book["rnbqkbnr/ppp2ppp/4p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -"] = [
            "b1c3", "g1f3", "c4d5"
        ]
        
        # King's Indian Defense: 1. d4 Nf6 2. c4 g6
        book["rnbqkb1r/pppppp1p/5np1/8/2PP4/8/PP2PPPP/RNBQKBNR w KQkq -"] = [
            "b1c3", "g1f3", "g2g3"
        ]
        
        # Nimzo-Indian: 1. d4 Nf6 2. c4 e6 3. Nc3 Bb4
        book["rnbqk2r/pppp1ppp/4pn2/8/1bPP4/2N5/PP2PPPP/R1BQKBNR w KQkq -"] = [
            "e2e3", "d1c2", "g1f3"
        ]
        
        # After 1. c4 (English Opening)
        book["rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq c3"] = [
            "e7e5", "g8f6", "c7c5", "e7e6"
        ]
        
        # After 1. Nf3
        book["rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -"] = [
            "d7d5", "g8f6", "c7c5", "e7e6"
        ]
        
        # After 1. Nf3 d5 2. d4
        book["rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq d3"] = [
            "g8f6", "e7e6", "c7c5", "b8c6"
        ]
        
        return book
    
    def get_book_move(self, board):
        """
        Get a move from the opening book for the current position
        
        Args:
            board: chess.Board object
            
        Returns:
            chess.Move or None: A book move if available, otherwise None
        """
        # Get FEN without move counts (only first 4 fields)
        fen_parts = board.fen().split(' ')
        position_fen = ' '.join(fen_parts[:4])
        
        # Check if position is in book
        if position_fen in self.book:
            book_moves_uci = self.book[position_fen]
            
            # Filter to only legal moves
            legal_book_moves = []
            for move_uci in book_moves_uci:
                try:
                    move = chess.Move.from_uci(move_uci)
                    if move in board.legal_moves:
                        legal_book_moves.append(move)
                except:
                    continue
            
            # Return a random move from the book
            if legal_book_moves:
                return random.choice(legal_book_moves)
        
        return None
    
    def is_in_book(self, board):
        """
        Check if the current position is in the opening book
        
        Args:
            board: chess.Board object
            
        Returns:
            bool: True if position is in book, False otherwise
        """
        fen_parts = board.fen().split(' ')
        position_fen = ' '.join(fen_parts[:4])
        return position_fen in self.book
    
    def get_book_size(self):
        """Get the number of positions in the opening book"""
        return len(self.book)
