# Unit Test Plan

This document outlines the plan for writing unit tests for the "concentrate" project. The goal is to ensure the core functionality of the application is working as expected after the migration to Python 3.13.  In addition, these tests will serve as regression tests for future code refactoring and new features.

## Testing Strategy

We will focus on testing the modules that contain the core logic of the application. The tests will be written using Python's built-in `unittest` framework. We will create a `tests` directory to store the test files.

### 1. `player.py`

This module is the most critical as it contains the game logic and the AI for the players. We will create a `test_player.py` file to test the `player0` and `player1` classes.

**Key areas to test:**

*   **`__init__`**:
    *   Verify that the wordlists (`wordlist`, `reducedlist`) are loaded correctly.
    *   Verify that the `neighbors` dictionary is created correctly.
*   **`possible(self, letters)`**:
    *   Test with a known set of `letters` and a small, controlled dictionary to ensure it returns the correct list of possible words.
    *   Verify that the cache (`self.cache`) is populated correctly after the first call and that the cached result is returned on subsequent calls.
*   **`concentrate(self, allletters, needletters, notletters, anyletters)`**:
    *   Test the filtering logic with various combinations of `needletters`, `notletters`, and `anyletters`.
    *   Verify that it correctly removes prefixes of already played words.
*   **`evaluatepos(self, allletters, blue, red)`**:
    *   Test with simple, known board positions to verify the score calculation.
    *   Test a game-over scenario to ensure it returns the correct win/loss score.
*   **`convertboardscore(self, rbscore)`**:
    *   Test with sample board strings to ensure it produces the correct `blue`, `red`, `bluedef`, and `reddef` bitmaps.
*   **`displayscore(self, blue, red)`**:
    *   Test with known `blue` and `red` bitmaps to ensure it produces the correct board string representation.
*   **`centroid(self, map)`**:
    *   Test with simple bitmaps to ensure it calculates the geometric center correctly.
*   **`defended_map(self, posmap)`**:
    *   Test with a simple position map to ensure it correctly identifies defended squares.
*   **`playissafe(self, group, play)`**:
    *   Test with hand-crafted word groups and plays to verify the logic for identifying "safe" moves.

### 2. `evolve.py`

This module contains the evolutionary algorithm for tuning the AI parameters. We will create a `test_evolve.py` file to test the helper functions.

**Key areas to test:**

*   **`mutate(parent)`**:
    *   Verify that the output has the same length as the input.
*   **`sex(parent1, parent2)`**:
    *   Test with two known parent tuples to ensure it returns their average.

### 3. `arena.py`

This module orchestrates games between players. We will create a `test_arena.py` file to test the helper functions.

**Key areas to test:**

*   **`genletters()`**:
    *   Verify that it returns a string of 25 uppercase letters and that the vowel count is within the specified range.
*   **`numscore(board)`**:
    *   Test with a sample board string to ensure it correctly counts the scores for blue and red.



