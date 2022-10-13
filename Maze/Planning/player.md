TO: CS4500

FROM: Diana Rodriguez and Thomas Mactaggart

DATE: 10/12/2022

SUBJECT: Player

To create a Player, we will need to obscure some data from each individual
(i.e. the opposing Player's goals), while also providing read only access to other data such
as certain aspects of the state of the board (their location, goal location etc.). To do this we plan to 
delegate information to players via the Game State which will act as our ground truth. Players will in turn send back
requests to perform tasks which may or may not be executed by the Referee.

In order to represent a Player we intend to make a class which contains pertinent information about a player. 
A player can be created with a home, goal, and an avatar. Each of these fields should be accessible by the Game State 
via getter methods. The current tile for a player will be its home Tile when created and will be accessible via a getter
and mutable via a setter allowing the Referee to move a player if needed.

A Player has:

- home_tile : Tile
- goal_tile : Tile
- current_tile : Tile
- avatar : Path

In terms of functionality, methods will be created to request a slide, request to rotate the spare tile,
and request to move around the board. The player receives information but does not initiate that conversation 
with the Referee.

The Player will have the following methods:

- get_home_tile() -> Tile
- get_goal_tile() -> Tile
- get_current_tile() -> Tile
- set_current_tile(Tile) -> None

Assume Referee will validate the order of these moves, Players can request the following moves in whatever order they 
like:
- request_slide_and_insert(int, Direction) -> None

  - Requests the Referee to move a row or column on the Board in the given Direction and insert the Board's spare Tile
- request_rotate(int) -> None

  - Requests the Referee to rotate the Board's spare Tile
- request_move_to(Tile) -> None

  - Requests the Referee to move this Player to the given Tile 

Thank you,

Diana and Thomas
