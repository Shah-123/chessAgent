# ♟️ ChessMastermind / Chess AI Agent

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25+-red.svg)

A sophisticated, full-stack Chess Engine and application built entirely in Python. **ChessMastermind** features a highly optimized custom AI utilizing advanced search algorithms and nuanced positional heuristics. The project provides two distinctive environments to play: an interactive, data-rich **Streamlit Dashboard** and a sleek **FastAPI backend** serving a vanilla HTML/JS frontend.

---

## 🚀 Engine Capabilities & Architecture

The core of ChessMastermind is built from scratch and implements competitive chess programming concepts to provide a formidable opponent.

### 🧠 Search Algorithm (`chess_engine.py`)
- **Minimax with Alpha-Beta Pruning**: Efficiently prunes the search tree to evaluate much deeper lines.
- **Iterative Deepening & Aspiration Windows**: Progressively searches deeper, reusing scores from previous iterations to narrow the initial alpha-beta window, drastically cutting down search times.
- **Quiescence Search**: Solves the "horizon effect" by continuing the search at the end of the main evaluation tree until all captures and checks are resolved.
- **Transposition Tables**: Caches previously evaluated board states (via FEN hashing) to avoid redundant calculations, storing exact scores, upper bounds, and lower bounds.
- **Advanced Move Ordering**: Sorts moves to maximize alpha-beta cutoffs:
  1. Transposition table best moves.
  2. **MVV-LVA** (Most Valuable Victim - Least Valuable Attacker) for captures.
  3. **Killer Move Heuristic**: Prioritizes moves that recently caused a cutoff at the same ply.
  4. **History Heuristic**: Boosts moves that have a high history of success across different branches.
  5. Bonuses for checks and pawn promotions.

### ⚖️ Positional Evaluation (`evaluation.py`)
The AI doesn't just calculate material; it deeply understands the positional aspects of the board.
- **Material Balance**: Standard centipawn valuations (P=100, N=320, B=330, R=500, Q=900).
- **Piece-Square Tables**: Dynamically guides pieces to their most active squares based on the game phase (e.g., King centralization in the Endgame vs King Safety in the Middlegame).
- **Pawn Structure Analysis**: Understands and evaluates doubled, isolated, and passed pawns.
- **King Safety**: Calculates the integrity of pawn shields and penalizes exposed kings.
- **Mobility & Center Control**: Rewards controlling the center (d4, d5, e4, e5) and overall legal move mobility.
- **Advanced Positional Factors**:
  - **Knight Outposts**: Identifies and rewards knights on strong squares protected by pawns and immune from enemy pawn attacks.
  - **Rook Activity**: Evaluates rook dominance on open, semi-open files, and the 7th rank.
  - **Piece Coordination**: Recognizes rook batteries and bishops holding long diagonals.
  - **Threat Detection**: Calculates attackers vs. defenders to identify hanging pieces.

### 📖 Opening Book (`opening_book.py`)
Includes a mapped FEN database covering a wide range of solid openings to guide the engine flawlessly through the first several moves, including:
- Ruy Lopez & Italian Game
- Sicilian, French, and Caro-Kann Defenses
- Queen's Gambit (Accepted & Declined)
- King's Indian & Nimzo-Indian Defenses
- English Opening & Reti

---

## 💻 Interfaces

ChessMastermind caters to different user preferences by exposing the engine through two distinct clients.

### 1. Streamlit Dashboard (`app.py`)
A comprehensive, data-rich environment meant for analysis and interactive play.
- **Features**: Visual SVG rendering of the board, real-time positional evaluation meters, move history tracking, captured pieces display, and dynamic difficulty adjustment.
- **Usage**: Type your moves using standard UCI notation (e.g., `e2e4`).


---

## 🛠️ Technology Stack

- **Python 3.11+**
- **python-chess**: Handling internal board state representation, move generation, and UCI parsing.
- **Streamlit**: For the dashboard UI (`app.py`).
- **FastAPI / Uvicorn**: For the API layer and the asynchronous web server (`web_app.py`).
- **NumPy**: Matrix/Array operations used heavily in the piece-square table evaluations.

---

## ⚙️ Installation & Setup

1. **Ensure Python 3.11+** is installed on your system.
2. **Clone the repository** and navigate to the project directory:
   ```bash
   cd ChessMastermind
   ```
3. **Install the dependencies**. The project utilizes `pyproject.toml` (and `uv.lock`). Use `pip` or `uv` to install:
   ```bash
   # Using pip
   pip install -e .
   
   # Using uv
   uv pip install -e .
   ```

---

## 🎮 How to Play

### Launching the Streamlit Interface
Best suited for a rich feature-set and analytic overlays.
```bash
streamlit run app.py
```
*Your browser will automatically open to `http://localhost:8501`. Configure the difficulty via the sidebar.*


## 📝 License
This project is open-source. Feel free to fork, optimize the evaluation logic, or expand the opening book!
