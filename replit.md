# Chess AI Application

## Overview

This is a chess game application built with Streamlit that allows users to play against an AI opponent. The application features a sophisticated chess engine with multiple difficulty levels, opening book knowledge, and advanced search algorithms. The AI uses minimax search with alpha-beta pruning, iterative deepening, quiescence search, and move ordering heuristics to find strong moves. The interface displays the chess board, tracks game history, shows captured pieces, and provides an interactive playing experience.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology Stack**: Streamlit web framework

The application uses Streamlit for the user interface, providing a reactive web-based chess board. The UI is session-based, storing game state (board position, move history, captured pieces, AI thinking status) in Streamlit's session state. This allows the application to maintain state across user interactions without requiring a traditional backend database.

**Design Pattern**: The frontend follows a component-based approach where the main application file (`app.py`) handles UI rendering and user interactions, delegating chess logic to specialized modules.

### Backend Architecture

**Chess Engine Design**: The backend is organized into three specialized modules:

1. **Chess Engine** (`chess_engine.py`): Implements the AI decision-making using:
   - Minimax algorithm with alpha-beta pruning for move search
   - Iterative deepening to improve time management
   - Transposition tables for position caching (max 1M entries)
   - Killer move heuristic and history heuristic for move ordering
   - Quiescence search to avoid horizon effects

2. **Position Evaluator** (`evaluation.py`): Provides static position evaluation using:
   - Material counting with standard piece values (P=100, N=320, B=330, R=500, Q=900)
   - Piece-square tables for positional bonuses
   - Additional heuristics for piece positioning and basic tactics

3. **Opening Book** (`opening_book.py`): Contains pre-programmed opening moves for popular variations (Spanish, Italian, Sicilian, French defenses, etc.). The AI consults this book before calculating moves to play theoretically sound openings.

**Rationale**: This modular separation allows each component to be developed, tested, and optimized independently. The chess engine can focus on search algorithms while the evaluator handles position assessment.

### Core Libraries

**Python Chess Library**: The application leverages the `python-chess` library for:
- Board representation and move generation
- Legal move validation
- Game state management (check, checkmate, stalemate detection)
- FEN notation handling

This library provides a robust, well-tested foundation rather than implementing chess rules from scratch.

### State Management

**Session-Based State**: All game state is stored in Streamlit's `st.session_state`:
- Current board position
- Game history (list of moves)
- Captured pieces for both sides
- AI computation status
- Game over conditions and results
- Selected square for move input

**Alternatives Considered**: Traditional database storage was considered but rejected because:
- Games are ephemeral (no persistence requirement)
- Session state provides sufficient functionality
- Reduces complexity and external dependencies

## External Dependencies

### Core Libraries

1. **Streamlit**: Web framework for the user interface
   - Purpose: Provides reactive UI components and session management
   - Version: Not specified (should be pinned in requirements.txt)

2. **python-chess**: Chess logic and board representation
   - Purpose: Handles all chess rules, move generation, and validation
   - Critical for: Legal move checking, board state, FEN parsing

3. **NumPy**: Numerical operations
   - Purpose: Used for piece-square table calculations in position evaluation
   - Provides efficient array operations for evaluation heuristics

### Data Storage

**No External Database**: The application does not use any external database or persistence layer. All data is stored in-memory within the Streamlit session state. This design choice means:
- Games are not saved between sessions
- No user account system
- No game history persistence
- Simplified deployment with no database setup required

### APIs and Services

**No External APIs**: The application is self-contained with no external API dependencies. The chess AI runs entirely locally using the implemented algorithms and opening book.

### Potential Future Integrations

The architecture could be extended to include:
- Cloud chess engines (Stockfish API, Lichess API) for analysis
- User authentication for saving games
- Database integration (PostgreSQL, SQLite) for game persistence
- Online multiplayer capabilities via WebSocket connections