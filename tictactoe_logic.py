"""Tic-tac-toe game logic for the web browsing tool."""

from typing import List, Optional, Tuple


def create_empty_board() -> List[List[str]]:
    """Create an empty 3x3 tic-tac-toe board."""
    return [['', '', ''] for _ in range(3)]


def check_winner(board: List[List[str]]) -> Optional[str]:
    """
    Check if there's a winner on the board.
    
    Args:
        board: 3x3 game board
        
    Returns:
        'X' or 'O' if there's a winner, None otherwise
    """
    # Check rows
    for row in board:
        if row[0] and row[0] == row[1] == row[2]:
            return row[0]
    
    # Check columns
    for col in range(3):
        if board[0][col] and board[0][col] == board[1][col] == board[2][col]:
            return board[0][col]
    
    # Check diagonals
    if board[0][0] and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    
    return None


def is_board_full(board: List[List[str]]) -> bool:
    """Check if the board is full (no empty spaces)."""
    for row in board:
        for cell in row:
            if not cell:
                return False
    return True


def minimax(board: List[List[str]], depth: int, is_maximizing: bool, player: str, opponent: str) -> int:
    """
    Minimax algorithm for finding the best move.
    
    Args:
        board: Current game board
        depth: Current depth in the game tree
        is_maximizing: True if maximizing player's turn
        player: The player we're optimizing for ('X' or 'O')
        opponent: The opponent ('X' or 'O')
        
    Returns:
        Score for the current board position
    """
    winner = check_winner(board)
    
    if winner == player:
        return 10 - depth
    elif winner == opponent:
        return depth - 10
    elif is_board_full(board):
        return 0
    
    if is_maximizing:
        max_score = -1000
        for i in range(3):
            for j in range(3):
                if not board[i][j]:
                    board[i][j] = player
                    score = minimax(board, depth + 1, False, player, opponent)
                    board[i][j] = ''
                    max_score = max(score, max_score)
        return max_score
    else:
        min_score = 1000
        for i in range(3):
            for j in range(3):
                if not board[i][j]:
                    board[i][j] = opponent
                    score = minimax(board, depth + 1, True, player, opponent)
                    board[i][j] = ''
                    min_score = min(score, min_score)
        return min_score


def find_best_move(board: List[List[str]], player: str, opponent: str) -> Tuple[int, int]:
    """
    Find the best move for the player using minimax.
    
    Args:
        board: Current game board
        player: The player to find a move for ('X' or 'O')
        opponent: The opponent ('X' or 'O')
        
    Returns:
        Tuple of (row, column) for the best move
    """
    best_score = -1000
    best_move = (0, 0)
    
    for i in range(3):
        for j in range(3):
            if not board[i][j]:
                board[i][j] = player
                score = minimax(board, 0, False, player, opponent)
                board[i][j] = ''
                
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    
    return best_move


def board_to_string(board: List[List[str]]) -> str:
    """Convert board to a string representation."""
    rows = []
    for row in board:
        row_str = "|".join(cell if cell else " " for cell in row)
        rows.append(row_str)
    return "\n".join(rows)