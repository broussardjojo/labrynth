Pair: mactaggartt-rodriguezdia \
Commit: [ce0248c88a6cbef30483a6c44a895dabbbdeba0a](https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/tree/ce0248c88a6cbef30483a6c44a895dabbbdeba0a) \
Self-eval: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/c8ffad1f0c3901e30898f1c9b0567952e5de018d/5/self-5.md \
Score: 96/160    
Grader: Varsha Ramesh

20/20: Self-eval

40/50 player.PP: Player class should have the following methods with good names, signatures/types, and purpose statements:

- [0/10pt] name
- [10/10pt] propose board
- [10/10pt] setting up
- [10/10pt] take a turn
- [10/10pt] did I win

16/40 referee.PP must have following functions with good names, signatures/types, and purpose statements:

- [10/10pt] setting up the player with initial information
- [0/10pt] running rounds until the game is over
   - You are running turns and the while loop is difficult to follow through.
- [6/10pt] running a round, which must have functionality for
   - Points for honesty, you have explicitly mentioned it is not there.
- [0/10pt] score the game
   - Write a method that determines winners

20/20 Unit tests for running a game:

- [10/10pt] a unit test for the referee function that returns a unique winner
- [10/10pt] a unit test for the scoring function that returns several winners

`WARNING: Every referee call on the player should be protected against illegal behavior and infinite loops/timeouts/exceptions. This should be factored out into a single point of control.` 

0/30 interactive-player.md 

Description of gestures that

- [0/10pt] rotates the tile before insertion 
- [0/10pt] selects a row or column to be shifted and in which direction
- [0/10pt] selects the next place for the player's avatar
