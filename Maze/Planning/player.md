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

In terms of functionality, methods will be created to request a slide, request to rotate the spare tile,
and request to move around the board. The player receives information but does not initiate that conversation 
with the Referee.

The Player will have the following methods:

- get_home_tile() -> Tile
- get_goal_tile() -> Tile
- get_current_tile() -> Tile
- set_current_tile(Tile) -> None
- request_slide(int, Direction) -> None
- request_rotate(int) -> None
- request_move_to(Tile) -> None

Thank you,

Diana and Thomas
