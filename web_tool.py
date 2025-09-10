"""Web browsing tool for playing Tic-tac-toe online."""

import asyncio
import logging
import re
from typing import List, Optional
from dataclasses import dataclass

try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: playwright not installed. Web browsing features will not work.")
    print("Install with: pip install playwright && playwright install chromium")

from tictactoe_logic import (
    create_empty_board,
    check_winner,
    is_board_full,
    find_best_move,
    board_to_string,
)

logger = logging.getLogger(__name__)


@dataclass
class TicTacToeResult:
    """Result of a Tic-tac-toe game."""
    outcome: str  # "win", "loss", or "draw"
    board_state: str  # String representation of final board
    summary: str  # Human-readable summary
    secret_number: Optional[str] = None  # 14-digit secret number if found


class WebBrowser:
    """Tool for web browsing tasks, specifically playing Tic-tac-toe."""
    
    def __init__(self):
        """Initialize the web browser tool."""
        self.timeout = 30000  # 30 seconds timeout
        
    def is_tictactoe_request(self, query: str) -> bool:
        """
        Check if the query is asking to play Tic-tac-toe.
        
        Args:
            query: The user's query
            
        Returns:
            True if this is a Tic-tac-toe request
        """
        ttt_keywords = ['tic-tac-toe', 'tictactoe', 'tic tac toe', 'noughts and crosses', 'ttt', 'ttt.puppy9.com']
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in ttt_keywords)
    
    async def find_game_cells(self, page: Page) -> List:
        """
        Find the game cells on the Tic-tac-toe page.
        
        Args:
            page: The Playwright page object
            
        Returns:
            List of cell elements
        """
        # Try different selectors commonly used for Tic-tac-toe games
        selectors = [
            'button.square',  # React tutorial style
            'button.cell',
            '[role="gridcell"]',
            '.cell',
            '.square',
            'td.cell',
            'td.square',
            'div.cell',
            'div.square',
            'button[data-cell]',
            'button[data-square]',
        ]
        
        for selector in selectors:
            elements = await page.locator(selector).all()
            if len(elements) >= 9:
                logger.info(f"Found {len(elements)} cells using selector: {selector}")
                return elements[:9]
        
        # Fallback: try to find any 9 clickable elements
        elements = await page.locator('button').all()
        if len(elements) >= 9:
            logger.info(f"Found {len(elements)} buttons as fallback")
            return elements[:9]
            
        return []
    
    async def read_board_state(self, cells: List, page: Page) -> List[List[str]]:
        """
        Read the current board state from the page.
        
        Args:
            cells: List of cell elements
            page: The Playwright page object
            
        Returns:
            3x3 board representation
        """
        board = create_empty_board()
        
        for i, cell in enumerate(cells[:9]):
            row, col = divmod(i, 3)
            try:
                # Try to get the text content
                text = await cell.inner_text()
                text = text.strip().upper()
                
                # Check for X or O
                if 'X' in text:
                    board[row][col] = 'X'
                elif 'O' in text or '0' in text:
                    board[row][col] = 'O'
                else:
                    # Try to check aria-label or other attributes
                    aria_label = await cell.get_attribute('aria-label')
                    if aria_label:
                        aria_label = aria_label.upper()
                        if 'X' in aria_label:
                            board[row][col] = 'X'
                        elif 'O' in aria_label:
                            board[row][col] = 'O'
            except Exception as e:
                logger.debug(f"Error reading cell {i}: {e}")
                
        return board
    
    async def play_tictactoe(self, url: Optional[str] = None) -> TicTacToeResult:
        """
        Play a game of Tic-tac-toe on a web page.
        
        Args:
            url: URL of the Tic-tac-toe game (optional, uses default if not provided)
            
        Returns:
            Result of the game
        """
        if not PLAYWRIGHT_AVAILABLE:
            return TicTacToeResult(
                outcome="error",
                board_state="",
                summary="Playwright is not installed. Please install it to use web browsing features."
            )
        
        # Default URL if none provided
        if not url:
            url = "https://playtictactoe.org/"
        
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            try:
                context = await browser.new_context(
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()
                
                logger.info(f"Navigating to {url}")
                await page.goto(url, timeout=self.timeout)
                
                # Wait for the page to load
                await page.wait_for_load_state('networkidle', timeout=5000)
                
                # Initialize game state
                board = create_empty_board()
                player = 'X'  # We play as X
                opponent = 'O'
                max_moves = 20  # Maximum number of moves to prevent infinite loops
                
                for move_count in range(max_moves):
                    # Find game cells
                    cells = await self.find_game_cells(page)
                    if len(cells) < 9:
                        logger.warning("Could not find 9 game cells")
                        await page.wait_for_timeout(500)
                        continue
                    
                    # Read current board state
                    board = await self.read_board_state(cells, page)
                    logger.info(f"Board state:\n{board_to_string(board)}")
                    
                    # Check for game over
                    winner = check_winner(board)
                    if winner or is_board_full(board):
                        break
                    
                    # Find and make our move
                    row, col = find_best_move(board, player, opponent)
                    cell_index = row * 3 + col
                    
                    if cell_index < len(cells):
                        logger.info(f"Making move at position ({row}, {col})")
                        await cells[cell_index].click()
                        
                        # Wait for the move to register
                        await page.wait_for_timeout(500)
                        
                        # Read board after our move
                        board = await self.read_board_state(cells, page)
                        
                        # Check if game is over after our move
                        winner = check_winner(board)
                        if winner or is_board_full(board):
                            break
                        
                        # Wait for opponent's move
                        await page.wait_for_timeout(1000)
                        
                        # Read board after opponent's move
                        board = await self.read_board_state(cells, page)
                
                # Determine outcome
                winner = check_winner(board)
                secret_number = None
                
                if winner == player:
                    outcome = "win"
                    summary = "I won the game!"
                    
                    # Look for 14-digit secret number in the page
                    await page.wait_for_timeout(2000)  # Wait for any congratulation message
                    page_text = await page.content()
                    
                    # Search for 14-digit number pattern
                    secret_pattern = r'\b\d{14}\b'
                    secret_matches = re.findall(secret_pattern, page_text)
                    if secret_matches:
                        secret_number = secret_matches[0]
                        summary = secret_number  # Return just the number as requested
                        logger.info(f"Found secret number: {secret_number}")
                    
                elif winner == opponent:
                    outcome = "loss"
                    summary = "I lost the game."
                elif is_board_full(board):
                    outcome = "draw"
                    summary = "The game ended in a draw."
                else:
                    outcome = "incomplete"
                    summary = "The game did not complete."
                
                board_state = board_to_string(board)
                
                return TicTacToeResult(
                    outcome=outcome,
                    board_state=board_state,
                    summary=summary,
                    secret_number=secret_number
                )
                
            except Exception as e:
                logger.error(f"Error playing Tic-tac-toe: {e}", exc_info=True)
                return TicTacToeResult(
                    outcome="error",
                    board_state="",
                    summary=f"Error playing game: {str(e)}"
                )
            finally:
                await browser.close()
    
    async def browse(self, query: str) -> str:
        """
        Main entry point for web browsing tasks.
        
        Args:
            query: The browsing task to perform
            
        Returns:
            Result of the browsing task
        """
        if self.is_tictactoe_request(query):
            # Try to extract URL from the query
            url = None
            url_pattern = r'https?://[^\s]+'
            url_matches = re.findall(url_pattern, query)
            if url_matches:
                url = url_matches[0].rstrip('/')  # Remove trailing slash if present
                logger.info(f"Extracted URL from query: {url}")
            
            result = await self.play_tictactoe(url)
            return result.summary
        
        return "I can currently only play Tic-tac-toe. Please ask me to play Tic-tac-toe!"