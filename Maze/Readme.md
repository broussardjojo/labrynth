# Development and Testing

To run all unit tests for this Milestone run `./xtest`

To run an individual unit test file run `pytest path/to/file`

To run an individual unit test run `pytest path/to/file::test_function_name`

Before running unit tests you may need to run `make` to install project dependencies

When installing packages, ensure that the version is compatible with Python 3.6. The `requirements.txt`
in this directory contains the latest versions of `pytest` and its dependencies which supported Python 3.6.


# Components and Roadmap

The server side of Maze.com will use a `LoginManager` that authenticates TCP clients, creates
associated `APIPlayer` instances via a remote proxy pattern, and assigns them to a game.

When enough players have joined, the manager gives the players to a `Referee`, which then
runs the game, and reports the winners and cheaters to the `LoginManager`.

The `Referee` can also accept `Observers` which receive updates on every turn. The `Observer` is
trusted not to give away secrets, but the referee still shields itself from `Observer` methods
crashing or timing out.

- `Player`, `Referee`: milestone 5
- `Observer`: milestone 6
- `LoginManager`: future milestone


# Code Files

### Common/board.py

```python
class Board:
    """
    A Board is a representation of a Labyrinth game board of size N by N, defaulting to 7. A Board has a grid of Tiles
    and an extra Tile. The grid is 0-indexed, row majored, and board[0][0] represents the Tile at the top-left.
    spot on this Board.
    """

    def from_list_of_shapes(cls, shape_grid: List[List[Shape]], next_tile_shape: Shape,
                            treasure_provider: Optional[Callable[[int, int], Tuple[Gem, Gem]]] = None) -> "Board":
    def from_list_of_tiles(cls, tile_grid: List[List[Tile]], **kwargs) -> "Board":
    def from_random_board(cls, height: int = 7, width: int = 7, **kwargs) -> "Board":
    def get_width(self) -> int:
    def get_height(self) -> int:
    def slide_and_insert(self, index: int, direction: Direction) -> PositionTransitionMap:
    def can_slide_horizontally(self, index: int) -> bool:
    def can_slide_vertically(self, index: int) -> bool:
    def check_stationary_position(self, row: int, col: int) -> bool:
    def reachable_tiles(self, base_position: Position) -> Set[Position]:
    def get_tile_by_position(self, position: Position) -> Tile:
    def get_tile_grid(self) -> List[List[Tile]]:
    def get_next_tile(self) -> Tile:
```

### Common/direction.py

```python
class Direction(Enum):
    """
    An Enum representing one of the four directions a Tile can move: Up, Right, Down, or Left
    """

    def get_offset_tuple(self) -> Tuple[int, int]:
    def get_opposite_direction(self):
```

### Common/gem.py

```python
class Gem:
    """
    A Gem is a gem to collect in the game and has a name and image filepath.
    """

    def get_gem_filepath(self) -> Path:
```

### Common/observableState.py

```python
class ObservableState:
    """
    Base class for a State which only exposes information to untrusted users of this class. It does not give access to
    Player information or allow users to change the Board for this State.
    """

    def get_board(self) -> Board:
    def get_all_previous_non_passes(self) -> List[Tuple[int, Direction]]:
```

### Common/position.py

```python
class Position:
    """
    Represents a Position on a Board as a row and column, which represent row and column indices on a Board's tile grid,
    a 2-D List of Tiles.
    """

    def get_row(self) -> int:
    def get_col(self) -> int:
    def get_position_tuple(self) -> Tuple[int, int]:
```

### Common/position_transition_map.py

```python
class PositionTransitionMap:
    """
    Represents the coordinate transitions performed by a single slide, see Board.slide_and_insert
    """
    updated_positions: Dict[Position, Position]
    removed_position: Position
    inserted_position: Position
```

### Common/shapes.py

```python
class Shape(ABC):
    """
    A Shape is one of: Corner, Line, TShaped, or Cross and has four booleans representing paths that can be walked on
    """
    
    def get_orientation_tuple(self) -> ShapeTuple:
    def rotate(self, rotations: int) -> "Shape":
    def has_path(self, path_direction: Direction) -> bool:


class Corner(Shape):
    ...


class Line(Shape):
    ...


class TShaped(Shape):
    ...


class Cross(Shape):
    ...
```

### Common/state.py

```python
class State(ObservableState):
    """
    A State is a representation of a Labyrinth game game-state. A State has a Board, list of Players, and an active
    Player.
    """

    def from_board_and_players(cls, selected_board: Board, list_of_players: List[Player]):
    def rotate_spare_tile(self, degrees: int) -> None:
    def kick_out_active_player(self) -> None:
    def is_active_player_at_goal(self) -> bool:
    def did_active_player_win(self):
    def slide_and_insert(self, index: int, direction: Direction) -> None:
    def get_players(self) -> List[Player]:
    def can_active_player_reach_position(self, target_position: Position) -> bool:
    def get_active_player_index(self) -> int:
    def is_active_player_at_home(self) -> bool:
    def change_active_player_turn(self) -> None:
    def move_active_player_to(self, position_to_move_to: Position) -> None:
    def active_player_has_reached_goal(self) -> bool:
    def get_closest_players_to_victory(self) -> List[Player]:
    def get_active_player_position(self) -> Position:
    def get_active_player(self) -> Player:
```

### Common/thread_utils.py

```python
def gather_protected(future_list: "List[Future[T]]", timeout_seconds=DEFAULT_TIMEOUT) -> List[Maybe[T]]:
def await_protected(future: "Future[T]", timeout_seconds=DEFAULT_TIMEOUT) -> Maybe[T]:
```

### Common/tile.py

```python
class Tile:
    """
    A Tile is a game piece to make the board and has a Shape and two Gems.
    """

    def get_gems(self) -> List[Gem]:
    def get_shape(self) -> Shape:
    def same_gems_on_tiles(self, gem1: Gem, gem2: Gem) -> bool:
    def has_path(self, path_direction: Direction) -> bool:
    def rotate(self, rotations: int) -> None:
```

### Common/utils.py

```python
class Maybe(ABC, Generic[T]):
    """
    Represents a value that may or may not be present; these cases are implemented by Just and Nothing, respectively.
    """
    is_present: bool
    def get_or_throw(self, message: str = "Missing Value") -> T:


class Nothing(Maybe[T]):
    """
    Represents the case where a Maybe[T] is absent.
    """


class Just(Maybe[T]):
    """
    Represents the case where a Maybe[T] is present.
    """


def remove_gem_extension(filename: Path) -> str:
def generate_gem_list() -> List[str]:
def get_json_obj_list(input_data) -> List[Union[dict, str, int]]:
def coord_custom_compare(coord_one: dict, coord_two: dict) -> int:
def get_euclidean_distance_between(position_one: Position, position_two: Position) -> int:
def get_connector_from_shape(shape: Shape) -> JSONConnector:
```

### JSON/deserializers.py

```python
def get_position_from_json(json_coordinate: JSONCoordinate) -> Position:
def get_gems_from_json(gem_name_list: JSONTreasure) -> Tuple[Gem, Gem]:
def get_tile_from_json(tilekey: JSONConnector, treasure: JSONTreasure) -> Tile:
def get_tile_grid_from_json(board_dict: JSONBoard) -> List[List[Tile]]:
def get_player_details_from_json(json_player: JSONPlayer) -> Player:
def get_direction_from_json(direction_str: JSONDirection) -> Direction:
def get_previous_move_from_json(json_action: JSONAction) -> Tuple[int, Direction]:
def get_state_from_json_state(json_state: JSONState) -> State:
def get_referee_player_details_from_json(json_referee_player: JSONRefereePlayer) -> Player:
def get_state_from_json_referee_state(json_state: JSONRefereeState) -> State:
def get_strategy_from_json(json_strategy_designation: JSONStrategyDesignation) -> Strategy:
def get_api_player_from_json(json_player_spec_el: JSONPlayerSpecElement) -> APIPlayer:
def get_bad_api_player_from_json(json_bad_player_spec_el: JSONBadPlayerSpecElement) -> APIPlayer:
def get_api_player_list_from_bad_player_spec_json(json_bad_player_spec: JSONBadPlayerSpec) -> List[APIPlayer]:
def get_api_player_list_from_player_spec_json(json_player_spec: JSONPlayerSpec) -> List[APIPlayer]:
```

### JSON/serializers.py

```python
def direction_to_json(direction: Direction) -> JSONDirection:
def position_to_json(position: Position) -> JSONCoordinate:
def move_to_json(self: Move) -> JSONChoiceMove:
```

### Players/api_player.py

```python
class APIPlayer(ABC):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html.
    """
    def setup(self, state: Optional[State], goal_position: Position) -> Acknowledgement:
    def propose_board0(self, rows: int, columns: int) -> Board:
    def name(self) -> str:
    def take_turn(self, current_state: State) -> Union[Move, Pass]:
    def win(self, did_win: bool) -> Acknowledgement:
    

class LocalPlayer(APIPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html. It runs locally.
    """


class BadLocalPlayer(LocalPlayer):
    """
    A class that represents a client of the referee. It implements the logical interactions spec at
    https://course.ccs.neu.edu/cs4500f22/local_protocol.html. It runs locally, and runs correctly until one
    'bad method' is called, at which point it raises an exception by attempting '1 // 0'
    """
```

### Players/base_strategy.py

```python
class BaseStrategy(Strategy):
    """
    A BaseStrategy representing a general type of strategy which picks a target and tries every possible slide/insert
    and rotate to see if it's possible to reach it, then gets a new target and repeats, passing if there are no
    more targets to try.
    """

    def generate_move(self, current_state: ObservableState, current_position: Position,
                      target_position: Position) -> Union[Move, Pass]:
    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
    def possible_next_target_positions(self, board: Board) -> bool:
    def get_checked_positions(self) -> List[Position]:
```

### Players/euclid.py

```python
class Euclid(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """

    def possible_next_target_positions(self, board: Board) -> bool:
    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
```

### Players/move.py

```python
class Pass:
    """
    A Class representing a Passed move, this means there is no sliding, inserting, rotating, or avatar moving
    """

    def return_if_move_perform_action_if_pass(if_pass_perform_action: Callable[[], Any]) -> Any:
    def perform_move_or_pass(self, perform_move_action: "Callable[[Move], None]", perform_pass_action: "Callable[[Pass], None]") -> None:
    

class Move:
    """
    A Class representing a Move which is valid move consisting of a slide index, slide Direction,
     spare tile rotation (in degrees), and a Position for the avatar to move to
    """

    def get_slide_index(self) -> int:
    def get_slide_direction(self) -> Direction:
    def get_spare_tile_rotation_degrees(self) -> int:
    def get_destination_position(self) -> Position:
    def return_if_move_perform_action_if_pass(self, if_pass_perform_action: Callable[[], Any]):
    def perform_move_or_pass(self, perform_move_action: "Callable[[Move], None]", perform_pass_action: "Callable[[Pass], None]") -> None:
```

### Players/player.py

```python
class Player:
    """
    A Player is a representation of a player of a game of Labyrinth. A Player has a home position, a goal position and a
    current position, which defaults to their home position.
    """

    def from_home_goal_color(cls, home_position: Position, goal_position: Position, color: str):
    def from_current_home_color(cls, current_position: Position, home_position: Position, color: str):
    def get_home_position(self) -> Position:
    def get_goal_position(self) -> Position:
    def set_goal_position(self, new_position: Position) -> None:
    def get_current_position(self) -> Position:
    def set_current_position(self, new_position: Position) -> None:
    def get_color(self) -> str:
```

### Players/riemann.py

```python
class Riemann(BaseStrategy):
    """
    A strategy which checks all possible ways to get the goal Position, then checks all possible Positions on the grid
    from top left to bottom right row by row as secondary goal Positions.
    """

    def possible_next_target_positions(self, board: Board) -> bool:
    def get_next_target_position(self, board: Board, original_target: Position) -> Position:
```

### Players/strategy.py

```python
class Strategy(ABC):
    """
    A Strategy which represents a decision system to determine a Move. A strategy is an abstract class which could be
    implemented in any number of ways depending on the Player's AI of choice
    """

    def generate_move(self, current_state: ObservableState,
                      current_position: Position,
                      target_position: Position) -> Union[Move, Pass]:
```

### Referee/observer.py

```python
class Observer:
    """
    Represents an Observer for a game of Labyrinth. An observer can display a given State of the game.
    """

    def receive_new_state(self, next_state: State) -> None:
    def set_game_is_over(self) -> None:
    def display_gui(self) -> None:
```

### Referee/referee.py

```python
class Referee:
    """
    A class representing a Referee for a game of Labyrinth. A referee is an arbiter of the game and is responsible for
    running the game to completion. The referee can handle the following abnormal interactions:
    - Player taking too long to propose a Move
    - Player provides invalid rotate
    - Player provides invalid slide
    - Player provides a slide-insert interaction that undoes the previous Move
    - Player provides a destination that is not on the board
    - Player provides a destination they cannot reach using their proposed Move
    We leave the following abnormal interactions to the remote communication phase of the game:
    - Player taking too long to propose a Board
    - Player proposing invalid Board (either invalid size or invalid by some future determination i.e. "unfair" or bad
    for game play)
    """

    def add_observer(self, observer: Observer) -> None:
    def run_game(self, clients: List[APIPlayer]) -> GameOutcome:
    def run_game_from_state(self, players: List[APIPlayer], game_state: State) -> GameOutcome:
    def get_proposed_board(clients: List[APIPlayer]) -> Board:
    def send_state_updates_to_observers(self, game_state: State) -> None:
    def send_game_over_to_observers(self) -> None:
```

# Other Files

## generate_readme.py
Generates the "Code Files" portion of this README (it still needs to be edited afterward)

## Harnesses
Folder containing integration test harnesses for milestones

## Resources
Folder containing resources such as images

### gems
Folder containing all images of gems

#### gemCollections
Folder containing images of pages of gems (not valid gems but provided in the tar file)

#### gem-name.png
Many files containing images of valid gems
