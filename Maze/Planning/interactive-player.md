TO: CS4500

FROM: Diana Rodriguez and Thomas Mactaggart

DATE: 10/27/2022

SUBJECT: Interactive Player

To create an interactive player mechanism, we will follow the principals from Fundamentals III and create a graphical
user interface, or view. This will be a view on the InformationalState. The InformationalState will extend an
ObservableState and be extended by a State. An InformationalState will have information about the board and its players.
Our current design does not allow for the player's information regarding goal Position, home Position, and current 
Position to be split across States, so we will need to modify our Player data definition to allow ensure the view does
not receive information about a Player's goal, because the view should not show Players' goal positions since other 
Players should not have access to this information.


A InformationalView has:

- InformationalState


An InformationalState has:

- board : Board
- list_of_players: List[InformationalPlayer]


An InformationalPlayer has:

- current_position: Position
- home_position: Position
- color: String
- name: String

In terms of functionality, the InformationalView should have methods to draw the InformationalState's Board and Players.

The InformationalView will have the following methods:

- draw_board() -> None
- draw_tile(shape: Shape, gem1: Gem, gem2: Gem) -> None
- draw_all_players() -> None
- draw_home(where_to_draw: Position, color: str, name: str) -> None
- draw_avatar(where_to_draw: Position, color: str, name: str) -> None

The InformationalState will have the following methods:

- get_board() -> Board
- get_players() -> List[InformationalPlayer]

The InformationalPlayer will have the following methods:

- get_current_position() -> Position
- get_home_position() -> Position
- get_color() -> str
- get_name() -> str

Thank you,

Diana and Thomas
