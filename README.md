Concentrate
===========

Letterpress AI

- player.py  
Main engine module, but not used directly.  Other modules depend on it

- reduced dict.py  
This takes 3esl.txt and en14.txt as input and makes reduced.txt.  Reduced.txt and en14.txt are used by the player.py to determine valid words.  The difference is that reduced.txt tries to simulate a (somewhat advanced) layman, as opposed to en14.txt, which is someone who knows basically every word in the English language.

- search.py  
Two functions are useful for displaying the results of the ai analysis: turn('letters','score') and easy('letters','score').  These use the full and reduced word lists, respectively.   These use two objects declared in the module, h (for hard) and e (for easy).  These objects inherit some useful methods from their parent, defined in player.py.  h.concentrate('letters',needletters='asdf',anyletters='qwer') would display all the words that use A, S, D and F and also Q, W, E, or R.  or you can write "s.concentrate('letters',anyletters='WX')" which will show you all the words that use W, or X, or both.  The second and third parameters are optional. 

- arena.py  
This was created to test minor changes to Concentrate, whether they improve or reduce the strength of the program.  Results of arena running are in the tests folder.  
The simplest function is just game().  This creates a game between player0 and player1, both defined in player.py, where player0 is the one that search.py uses, and player1 is the modification.  Game can accept a board or generate one if none is passed in, another parameter controls whether player0 goes first or not.  It will display each move played, the board as it looks after that move is played, and the current score with the number of defended squares in parentheses. Match() builds on top of game() by calling game() twice with the same (optionally passed in) board so that both players go first once on the same board.  Finally tournament(n) calls match n times for n randomly generated boards and sums the results, displaying the grand total at the end to see who won.  

- GUI.py  
Press Tab or use the menu item in options to switch between two modes: playing against Concentrate, and analyzing a game with Concentrate.  
The five difficulty settings: Dunce, Easy, Medium, Hard, Extreme.  Extreme always plays the best word according to the AI's evaluation from the complete letterpress word list.  The other difficulty settings use a reduced word list, meant to simulate a layman's vocabulary.  Hard chooses the best word it can find from the reduced word list.  Medium chooses the best word of 8 letters or fewer from the reduced word list.  Easy chooses the best word of 5 letters or fewer from the reduced word list.  Dunce chooses a random word 8 letters or less from the reduced word list.  
  - Play Against mode  
  You play blue, Concentrate plays red.  Click letters to form a word, and press the Play button.  Press the pass button to pass.  Select a word in the game history to continue from that point in the game (a way to take back a move).
  - Analyze mode  
  Typing when the board is selected allows you to change the board.  Clicking a square on the board changes the color of that board.  
  Click the search button with the search box blank to show the best 200 words in the results box.  If you type letters in the search box and search, only words with those letters will appear in the search box.  Typing "-" before a group of letters allows for the exclusion of those letters from the search.
  Note: only words which can change the score are shown.  And, if a word can be played multiple ways, only ways which change the score the most are displayed.  For example, if there are two Ts, but one is defended, TOP will be shown with only the T that is undefended.  


  
