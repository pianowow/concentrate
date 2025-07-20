Concentrate
============

Letterpress AI

- player.py  
  Main engine module, but not used directly.  Other modules depend on it

- GUI.py  
  Run this to view the graphical user interface for concentrate.  
  Press Tab or use the menu item in options to switch between two modes: playing against Concentrate, and analyzing a game with Concentrate.  
  The five difficulty settings: Dunce, Easy, Medium, Hard, Extreme.  Extreme always plays the best word according to the AI's evaluation from the complete letterpress word list.  The other difficulty settings use a reduced word list, meant to simulate a layman's vocabulary.  Hard chooses the best word it can find from the reduced word list.  Medium chooses the best word of 8 letters or fewer from the reduced word list.  Easy chooses the best word of 5 letters or fewer from the reduced word list.  Dunce chooses a random word 8 letters or less from the reduced word list.  
  
  - Analyze mode  
    Typing when the board is selected allows you to change the board.  Clicking a square on the board changes the color of that board.  
    Double-click the word "Board" in the GUI to get a peek into how Concentrate evaluates a position.  
    Click the search button with the search box blank to show the best 200 words in the results box.  If you type letters in the search box and search, only words with those letters will appear in the search box.  Typing "-" before a group of letters allows for the exclusion of those letters from the search.  Scroll to the bottom and choose "More" to get the next 200 words.  
    Note: only words which can change the score are shown.  A word that can only use defended letters is omitted.  
    Words in the search results box are color-coded:
    - Black: _Standard_ moves with no immediate special conditions.
    - Red: _Losing_ moves. Playing a red word gives the opponent a guaranteed win on their next turn.
    - Green: _Ending soon_ moves. Playing a green word allows the opponent to end the game on their next turn, but if they do you win.
  - Play Against mode  
    You play blue, Concentrate plays red.  Click letters to form a word, and press the Play button.  Click the word formed below if you want to clear your selection.  Press the pass button to pass.  Select a word in the game history to continue from that point in the game (a way to take back a move).  

- evolve.py  
  This module was created to determine the appropriate value for various weights in concentrate's evaluation function.  It uses an evolutionary algorithm to create multiple versions of concentrate with different weights, and they play against each other.  The strongest survive and new members are generated.  
  Please note this is set to spawn 3 python processes (multiprocessing.Pool) to speed things up, so if you have a single or dual core system, this may not play nice.  

- arena.py  
  This was created to test minor changes to Concentrate, whether they improve or reduce the strength of the program.
  The simplest function is just game().  This creates a game between player0 and player1, both defined in player.py, where player0 is the one that the GUI uses, and player1 is the modification being tested.  Game() can accept a board or generate one if none is passed in, another parameter controls whether player0 goes first or not.  It will display each move played, the board as it looks after that move is played, and the current score with the number of defended squares in parentheses. Both() builds on top of game() by calling game() twice with the same (optionally passed in) board so that both players go first once on the same board.  Finally match(n) calls both() n times for n randomly generated boards and sums the results, displaying the grand total at the end to see who won.  

- search.py  
  Command line interface for viewing possible words to play in a position.  
  Two functions are useful for displaying the results of the ai analysis: turn('letters','score') and easy('letters','score').  These use the full and reduced word lists, respectively.   'letters' should be all 25 letters, top left to bottom right, like this: 'FACHXGHWVUTVRTMWYNBAITROA', and 'score' is the same but with B for blue, R for red, anything else not R, B or a number for an unclaimed letter.  A single digit can follow any character in score to represent how many of them to repeat.  For example 'B5B5W5R5R5' would represent blue occupying the top two rows, red the bottom two.  

- 

## Contributing

To set up your development environment and start contributing, follow these steps:

1. **Clone the repository:**
   
   ```bash
   git clone https://github.com/pianowow/concentrate.git
   cd concentrate
   ```

2. **Install uv:**
   If you don't have `uv` installed, you can install it via `pipx` (recommended) or your system's package manager. For Arch Linux users, it's available in the official repositories.
   Using pipx (if you don't have it, install with 'pip install pipx')
   
   ```bash
   pipx install uv
   ```
   
   Or via your system's package manager (e.g., for Arch Linux)
   
   ```bash
   > sudo pacman -S uv
   ```

3. **Create and activate the virtual environment:**
   `uv` can create virtual environments directly.
   
   ```bash
   uv venv
   source .venv/bin/activate
   ```

4. **Install dependencies:**
   Once your virtual environment is active, install the project dependencies using `uv pip sync`. This will install all packages listed in `requirements.lock`.
   
   ```bash
   uv pip sync requirements.lock
   ```

### Understanding `requirements.txt` and `requirements.lock`

This project uses both `requirements.txt` and `requirements.lock` for dependency management. Here's why:

* **`requirements.txt`**: This file lists the project's **direct dependencies** and could include version ranges (e.g., `requests>=2.20`). It's meant to be human-readable and defines the *high-level requirements* for the project. You'll typically modify this file when adding or removing primary dependencies.

* **`requirements.lock`**: This file "pins" the **exact versions** of *all* dependencies—both direct and transitive—that were successfully installed and worked together at a specific point in time. It's machine-generated by `uv pip compile` and ensures **reproducible builds**. This file should generally *not* be manually edited.

**Workflow for managing dependencies:**

1. **To add or update a direct dependency:** Modify `requirements.txt` with the desired package and version.
2. **To update `requirements.lock`:** Run `uv pip compile requirements.txt -o requirements.lock`. This will resolve all dependencies and write their exact versions to `requirements.lock`.
3. **To sync your environment:** Run `uv pip sync requirements.lock` to install the exact versions specified in the lock file into your virtual environment.
