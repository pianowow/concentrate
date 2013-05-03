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
A work in progress, but this will end up being the front-facing side of the released application.  