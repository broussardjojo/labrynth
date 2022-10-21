TO: CS4500

FROM: Diana Rodriguez and Thomas Mactaggart

DATE: 10/20/2022

SUBJECT: Player Protocol

The communication between the player components and the referee should adhere to the following protocol:

To set up the game, the referee should add players to the game, assigning each a goal and home tile. The referee should
use the add_player() method on the State to add unique players to the game.

Next, to begin the game, the referee should request a move from the active player by calling the get_next_move() method 
on the player, giving the player an ObservableState to do so. A player will, in turn, return a Move, which consists of a
slide index, slide direction, spare tile rotation in degrees, and target position. 

Next, the referee will validate the player's requested move based on its rule set. This will be done by using the method
validate_move(), which will take in the potential Move and the current State of the game. If the Move is valid, the
referee should implement the move. 

To implement the Move, the referee will first call the rotate_spare_tile() method on the State, providing it the rotation 
in degrees. Next, the referee will call the slide_and_insert() method on the State, providing it the requested slide 
index and slide direction. Next, the referee will call the move_active_player_to() method on the State, providing it the 
requested target Position. 

After performing the Move, the referee will call the is_game_over() method on the State which will check if either end condition
has been met (the active_player has acquired their Gems and returned home or all players have passed). 

If the game has not ended, the referee will call the change_active_player_turn() method on the State.

If the requested Move was invalid, the referee will call the kick_out_active_player() method.

The referee will repeat these instructions until the game has ended. Once the game has ended, the referee will communicate the results
to all participants.

Thank you,
Thomas and Diana