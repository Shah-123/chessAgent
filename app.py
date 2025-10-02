import streamlit as st
import chess
import chess.svg
from chess_engine import ChessAI
from evaluation import PositionEvaluator

def initialize_game():
    """Initialize a new chess game"""
    if 'board' not in st.session_state:
        st.session_state.board = chess.Board()
    if 'game_history' not in st.session_state:
        st.session_state.game_history = []
    if 'captured_pieces' not in st.session_state:
        st.session_state.captured_pieces = {'white': [], 'black': []}
    if 'ai_thinking' not in st.session_state:
        st.session_state.ai_thinking = False
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'result' not in st.session_state:
        st.session_state.result = None
    if 'selected_square' not in st.session_state:
        st.session_state.selected_square = None
    if 'ai_engine' not in st.session_state:
        st.session_state.ai_engine = ChessAI()

def reset_game():
    """Reset the game to initial state"""
    st.session_state.board = chess.Board()
    st.session_state.game_history = []
    st.session_state.captured_pieces = {'white': [], 'black': []}
    st.session_state.ai_thinking = False
    st.session_state.game_over = False
    st.session_state.result = None
    st.session_state.selected_square = None

def get_piece_unicode(piece):
    """Get Unicode symbol for chess piece"""
    piece_symbols = {
        (chess.PAWN, chess.WHITE): '♙',
        (chess.KNIGHT, chess.WHITE): '♘',
        (chess.BISHOP, chess.WHITE): '♗',
        (chess.ROOK, chess.WHITE): '♖',
        (chess.QUEEN, chess.WHITE): '♕',
        (chess.KING, chess.WHITE): '♔',
        (chess.PAWN, chess.BLACK): '♟',
        (chess.KNIGHT, chess.BLACK): '♞',
        (chess.BISHOP, chess.BLACK): '♝',
        (chess.ROOK, chess.BLACK): '♜',
        (chess.QUEEN, chess.BLACK): '♛',
        (chess.KING, chess.BLACK): '♚',
    }
    return piece_symbols.get((piece.piece_type, piece.color), '')

def render_board_svg():
    """Render chess board as SVG"""
    board = st.session_state.board
    svg = chess.svg.board(
        board=board,
        size=400,
        lastmove=board.peek() if board.move_stack else None,
        check=board.king(board.turn) if board.is_check() else None
    )
    return svg

def make_ai_move(difficulty):
    """Make AI move and update game state"""
    if not st.session_state.game_over and not st.session_state.board.turn:
        with st.spinner('AI is thinking...'):
            best_move = st.session_state.ai_engine.get_best_move(st.session_state.board, difficulty)
            
            if best_move:
                if st.session_state.board.is_capture(best_move):
                    captured_piece = st.session_state.board.piece_at(best_move.to_square)
                    if captured_piece:
                        st.session_state.captured_pieces['white'].append(captured_piece)
                
                st.session_state.board.push(best_move)
                st.session_state.game_history.append(best_move)
                
                if st.session_state.board.is_game_over():
                    st.session_state.game_over = True
                    st.session_state.result = st.session_state.board.result()

def main():
    st.set_page_config(page_title="Chess AI Agent - Stockfish-like Engine", layout="wide", page_icon="♟")
    
    st.title("♟ Chess AI Agent")
    st.markdown("**Play against a strong AI using minimax search with alpha-beta pruning**")
    
    initialize_game()
    
    with st.sidebar:
        st.header("⚙️ Game Controls")
        
        difficulty = st.selectbox(
            "AI Strength",
            options=[2, 3, 4, 5],
            index=2,
            format_func=lambda x: f"Level {x-1} ({x} ply)",
            help="Higher levels search deeper and play stronger"
        )
        
        if st.button("🔄 New Game", use_container_width=True):
            reset_game()
            st.rerun()
        
        st.divider()
        st.header("📊 Game Status")
        
        if st.session_state.game_over:
            result = st.session_state.result
            if result == "1-0":
                st.success("✅ White wins!")
            elif result == "0-1":
                st.error("❌ Black wins!")
            else:
                st.info("🤝 Draw")
        else:
            turn = "White (You)" if st.session_state.board.turn else "Black (AI)"
            st.info(f"**Turn:** {turn}")
        
        if st.session_state.board.is_check():
            st.warning("⚠️ Check!")
        
        st.divider()
        st.header("🎯 Captured Pieces")
        
        st.subheader("By Black:")
        if st.session_state.captured_pieces['white']:
            captured = ' '.join([get_piece_unicode(p) for p in st.session_state.captured_pieces['white']])
            st.markdown(f"<h2>{captured}</h2>", unsafe_allow_html=True)
        else:
            st.write("None")
        
        st.subheader("By White:")
        if st.session_state.captured_pieces['black']:
            captured = ' '.join([get_piece_unicode(p) for p in st.session_state.captured_pieces['black']])
            st.markdown(f"<h2>{captured}</h2>", unsafe_allow_html=True)
        else:
            st.write("None")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("♟ Chess Board")
        
        board_svg = render_board_svg()
        st.image(board_svg, use_container_width=False)
        
        if not st.session_state.game_over:
            st.markdown("---")
            st.markdown("**Make your move:**")
            
            move_input_col1, move_input_col2 = st.columns([3, 1])
            
            with move_input_col1:
                move_input = st.text_input(
                    "Enter move (e.g., e2e4, e7e5, e1g1 for castling)",
                    key="move_input",
                    placeholder="e2e4",
                    label_visibility="collapsed"
                )
            
            with move_input_col2:
                make_move_btn = st.button("▶️ Move", use_container_width=True, type="primary")
            
            if make_move_btn and move_input and st.session_state.board.turn == chess.WHITE:
                try:
                    move = chess.Move.from_uci(move_input.strip())
                    
                    if move in st.session_state.board.legal_moves:
                        if st.session_state.board.is_capture(move):
                            captured_piece = st.session_state.board.piece_at(move.to_square)
                            if captured_piece:
                                st.session_state.captured_pieces['black'].append(captured_piece)
                        
                        st.session_state.board.push(move)
                        st.session_state.game_history.append(move)
                        
                        if st.session_state.board.is_game_over():
                            st.session_state.game_over = True
                            st.session_state.result = st.session_state.board.result()
                        else:
                            make_ai_move(difficulty)
                        
                        st.rerun()
                    else:
                        st.error("❌ Illegal move! Try again.")
                except (ValueError, chess.InvalidMoveError):
                    st.error("❌ Invalid move format! Use UCI notation (e.g., e2e4)")
            
            with st.expander("📝 Legal Moves Reference"):
                legal_moves = list(st.session_state.board.legal_moves)
                if legal_moves:
                    moves_text = ", ".join([move.uci() for move in sorted(legal_moves, key=lambda m: m.uci())])
                    st.code(moves_text, language="text")
                else:
                    st.write("No legal moves")
    
    with col2:
        st.subheader("📜 Move History")
        
        if st.session_state.game_history:
            moves_display = []
            for i in range(0, len(st.session_state.game_history), 2):
                move_num = i // 2 + 1
                white_move = st.session_state.game_history[i].uci()
                black_move = st.session_state.game_history[i + 1].uci() if i + 1 < len(st.session_state.game_history) else ""
                moves_display.append(f"{move_num}. {white_move:6s} {black_move}")
            
            move_history_text = "\n".join(moves_display)
            st.text_area("", value=move_history_text, height=200, disabled=True, label_visibility="collapsed")
        else:
            st.info("No moves yet")
        
        st.divider()
        st.subheader("⚖️ Position Evaluation")
        
        evaluator = PositionEvaluator()
        position_score = evaluator.evaluate_position(st.session_state.board)
        
        score_display = position_score / 100.0
        
        if position_score > 50:
            st.success(f"White advantage: +{score_display:.2f}")
        elif position_score < -50:
            st.error(f"Black advantage: {score_display:.2f}")
        else:
            st.info(f"Position: {score_display:+.2f}")
        
        progress_val = min(max((position_score + 1000) / 2000, 0), 1)
        st.progress(progress_val, text="Position balance")
        
        st.divider()
        st.subheader("ℹ️ Game Info")
        
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.metric("Moves", len(st.session_state.game_history))
            st.metric("Legal Moves", st.session_state.board.legal_moves.count())
        
        with info_col2:
            st.metric("Halfmoves", st.session_state.board.halfmove_clock)
            st.metric("Fullmoves", st.session_state.board.fullmove_number)
        
        with st.expander("🔧 Technical Details"):
            st.caption("FEN Notation:")
            st.code(st.session_state.board.fen(), language="text")
            
            st.caption("Board Status:")
            status = []
            if st.session_state.board.is_check():
                status.append("Check")
            if st.session_state.board.is_checkmate():
                status.append("Checkmate")
            if st.session_state.board.is_stalemate():
                status.append("Stalemate")
            if st.session_state.board.is_insufficient_material():
                status.append("Insufficient Material")
            if not status:
                status.append("In Progress")
            st.write(", ".join(status))

if __name__ == "__main__":
    main()
