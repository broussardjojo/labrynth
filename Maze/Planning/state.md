TO: CS4500

FROM: Diana Rodriguez and Thomas Mactaggart

DATE: 10/7/2022

SUBJECT: Game State

We believe the referee should have the following information: the current state of the board (included goal tiles and 
home tiles for each player), the number of players playing the game, whose turn it is, and what is 
considered to be a valid move.

In terms of data representation, the current state of the board will be represented by an instance of our Board class. The referee should have access to 
a list of all Players. We will use an Enum to represent whose turn it is at any given point in time. 

In terms of functionality, a method will be created to determine if a move is valid or not. We also will create a function
to change whose turn it is. Another function will be needed to determine if any player has won the game. We need a function
to announce the end of the game, as well as its outcome to the Players.

- is_valid_move() -> bool
- change_turn() -> None
- is_game_over() -> bool
- announce_game_over() -> None
- announce_outcome() -> None

Thank you,
Diana and Thomas
