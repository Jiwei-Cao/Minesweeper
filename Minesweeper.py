import random
import tkinter as tk
from tkinter import messagebox, simpledialog
from typing import List, Tuple, Set

class MinesweeperGUI:
    def __init__(self, master):
        self.master = master
        master.title("Minesweeper")
        
        # Game settings
        self.get_game_settings()
        
        # Initialize game
        self.game = Minesweeper(self.width, self.height, self.mines)
        
        # Create menu
        self.create_menu()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set(f"Mines: {self.mines} | Flags: 0")
        self.status_bar = tk.Label(master, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Create game board
        self.create_board()
    
    def get_game_settings(self):
        """Get game settings from user."""
        self.width = simpledialog.askinteger("Width", "Enter board width:", minvalue=5, maxvalue=30, initialvalue=10)
        if self.width is None:
            self.width = 10
            
        self.height = simpledialog.askinteger("Height", "Enter board height:", minvalue=5, maxvalue=20, initialvalue=10)
        if self.height is None:
            self.height = 10
            
        max_mines = self.width * self.height - 1
        default_mines = min(max_mines, self.width * self.height // 5)
        self.mines = simpledialog.askinteger("Mines", f"Enter number of mines (1-{max_mines}):", 
                                            minvalue=1, maxvalue=max_mines, initialvalue=default_mines)
        if self.mines is None:
            self.mines = default_mines
    
    def create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.master)
        
        # Game menu
        game_menu = tk.Menu(menubar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.new_game)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="Game", menu=game_menu)
        
        # Difficulty menu
        difficulty_menu = tk.Menu(menubar, tearoff=0)
        difficulty_menu.add_command(label="Beginner (9x9, 10 mines)", 
                                    command=lambda: self.set_difficulty(9, 9, 10))
        difficulty_menu.add_command(label="Intermediate (16x16, 40 mines)", 
                                    command=lambda: self.set_difficulty(16, 16, 40))
        difficulty_menu.add_command(label="Expert (30x16, 99 mines)", 
                                    command=lambda: self.set_difficulty(30, 16, 99))
        difficulty_menu.add_command(label="Custom...", command=self.custom_difficulty)
        menubar.add_cascade(label="Difficulty", menu=difficulty_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="How to Play", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)
    
    def create_board(self):
        """Create the game board with buttons."""
        # Create a frame for the board
        try:
            self.board_frame.destroy()
        except:
            pass
            
        self.board_frame = tk.Frame(self.master)
        self.board_frame.pack(padx=10, pady=10)
        
        # Calculate button size based on board dimensions
        button_size = min(30, max(15, int(600 / max(self.width, self.height))))
        
        # Create buttons for each cell
        self.buttons = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                button = tk.Button(self.board_frame, width=2, height=1, 
                                   font=('Arial', button_size // 3),
                                   command=lambda x=x, y=y: self.left_click(x, y))
                button.grid(row=y, column=x)
                button.bind("<Button-3>", lambda event, x=x, y=y: self.right_click(x, y))
                row.append(button)
            self.buttons.append(row)
    
    def left_click(self, x, y):
        """Handle left click (reveal cell)."""
        if not self.game.game_over:
            game_continues = self.game.reveal(x, y)
            self.update_board()
            
            if not game_continues:
                self.show_game_over()
    
    def right_click(self, x, y, event=None):
        """Handle right click (flag cell)."""
        if not self.game.game_over:
            self.game.toggle_flag(x, y)
            self.update_board()
    
    def update_board(self):
        """Update the GUI to reflect the current game state."""
        for y in range(self.height):
            for x in range(self.width):
                button = self.buttons[y][x]
                
                if self.game.revealed[y][x]:
                    button.config(relief=tk.SUNKEN, borderwidth=1)
                    if self.game.board[y][x] == 'X':
                        button.config(text="💣", bg='red')
                    elif self.game.board[y][x] == '0':
                        button.config(text="", bg='lightgray')
                    else:
                        # Set color based on number
                        colors = ['blue', 'green', 'red', 'purple', 'maroon', 'turquoise', 'black', 'gray']
                        number = int(self.game.board[y][x])
                        button.config(text=str(number), fg=colors[number-1], bg='lightgray')
                else:
                    if self.game.flagged[y][x]:
                        button.config(text="🚩")
                    else:
                        button.config(text="")
        
        # Update status bar
        flags = sum(row.count(True) for row in self.game.flagged)
        self.status_var.set(f"Mines: {self.mines} | Flags: {flags}")
        
        # Check for win condition
        if self.game.win:
            self.show_win()
    
    def show_game_over(self):
        """Show game over dialog."""
        # Reveal all mines
        for x, y in self.game.mine_positions:
            if not self.game.flagged[y][x]:
                self.buttons[y][x].config(text="💣", bg='red')
        
        # Show incorrect flags
        for y in range(self.height):
            for x in range(self.width):
                if self.game.flagged[y][x] and (x, y) not in self.game.mine_positions:
                    self.buttons[y][x].config(text="❌", bg='orange')
        
        messagebox.showinfo("Game Over", "You hit a mine! Game over.")
    
    def show_win(self):
        """Show win dialog."""
        messagebox.showinfo("Congratulations", "You won the game!")
    
    def new_game(self):
        """Start a new game with current settings."""
        self.game = Minesweeper(self.width, self.height, self.mines)
        self.update_board()
        # Reset button appearance
        for row in self.buttons:
            for button in row:
                button.config(text="", relief=tk.RAISED, borderwidth=2, bg='SystemButtonFace')
    
    def set_difficulty(self, width, height, mines):
        """Set game difficulty."""
        self.width = width
        self.height = height
        self.mines = mines
        self.game = Minesweeper(width, height, mines)
        self.create_board()
    
    def custom_difficulty(self):
        """Set custom difficulty."""
        self.get_game_settings()
        self.game = Minesweeper(self.width, self.height, self.mines)
        self.create_board()
    
    def show_help(self):
        """Show help dialog."""
        help_text = """
        How to Play Minesweeper:
        
        1. Left-click to reveal a cell
        2. Right-click to place or remove a flag
        3. Numbers show how many mines are adjacent
        4. Reveal all non-mine cells to win
        
        Good luck!
        """
        messagebox.showinfo("How to Play", help_text)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
        Minesweeper Game
        
        A classic game of minesweeper created with Python and Tkinter.
        
        Enjoy!
        """
        messagebox.showinfo("About", about_text)


class Minesweeper:
    def __init__(self, width: int = 10, height: int = 10, mines: int = 10):
        """Initialize a Minesweeper game.
        
        Args:
            width: Board width
            height: Board height
            mines: Number of mines
        """
        self.width = width
        self.height = height
        self.mines = min(mines, width * height - 1)
        self.board = [['0' for _ in range(width)] for _ in range(height)]
        self.revealed = [[False for _ in range(width)] for _ in range(height)]
        self.flagged = [[False for _ in range(width)] for _ in range(height)]
        self.game_over = False
        self.win = False
        self.first_move = True
        self.mine_positions: Set[Tuple[int, int]] = set()
    
    def place_mines(self, first_x: int, first_y: int):
        """Place mines randomly on the board, avoiding the first clicked position."""
        positions = [(x, y) for x in range(self.width) for y in range(self.height) 
                    if (x, y) != (first_x, first_y)]
        self.mine_positions = set(random.sample(positions, self.mines))
        
        # Place mines on the board
        for x, y in self.mine_positions:
            self.board[y][x] = 'X'
        
        # Calculate numbers for adjacent cells
        for x, y in self.mine_positions:
            for nx, ny in self._get_neighbors(x, y):
                if self.board[ny][nx] != 'X':
                    self.board[ny][nx] = str(int(self.board[ny][nx]) + 1)
    
    def _get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid neighbors of a cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    neighbors.append((nx, ny))
        return neighbors
    
    def reveal(self, x: int, y: int) -> bool:
        """Reveal a cell. Return True if the game continues, False if game over."""
        if self.game_over or self.flagged[y][x]:
            return True
            
        if self.first_move:
            self.place_mines(x, y)
            self.first_move = False
            
        if self.board[y][x] == 'X':
            self.revealed[y][x] = True
            self.game_over = True
            return False
            
        self._reveal_cell(x, y)
        
        # Check if player has won
        unrevealed = sum(row.count(False) for row in self.revealed)
        if unrevealed == self.mines:
            self.win = True
            self.game_over = True
            
        return True
    
    def _reveal_cell(self, x: int, y: int):
        """Recursively reveal a cell and its neighbors if it's a 0."""
        if self.revealed[y][x]:
            return
            
        self.revealed[y][x] = True
        
        # If this is a zero, reveal all neighbors
        if self.board[y][x] == '0':
            for nx, ny in self._get_neighbors(x, y):
                self._reveal_cell(nx, ny)
    
    def toggle_flag(self, x: int, y: int):
        """Toggle a flag on a cell."""
        if not self.revealed[y][x] and not self.game_over:
            self.flagged[y][x] = not self.flagged[y][x]


def main():
    root = tk.Tk()
    app = MinesweeperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()