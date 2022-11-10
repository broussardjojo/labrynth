from typing import Union, List, Optional
from typing_extensions import Literal, TypedDict

# ==========
# https://course.ccs.neu.edu/cs4500f22/3.html

# Interpretation: The shape of paths on one Tile
JSONConnector = Union[
    Literal["│"],
    Literal["─"],
    Literal["┐"],
    Literal["└"],
    Literal["┌"],
    Literal["┘"],
    Literal["┬"],
    Literal["├"],
    Literal["┴"],
    Literal["┤"],
    Literal["┼"],
]

# Interpretation: One of the gems that a Tile can contain
JSONGem = str

# Interpretation: A pair of gems on one Tile
# Constraint: The length of the list must be 2
JSONTreasure = List[str]


class JSONBoard(TypedDict):
    """
    Interpretation: Contains one Matrix for the connections
    that each tile realizes (an essential aspect for navigation) and
    one equally-sized matrix for the treasures each tile displays.
    """
    connectors: List[List[JSONConnector]]
    treasures: List[List[JSONTreasure]]


# Interpretation: Specifies a tile location. The row count starts at the top,
# the column count at the left.
JSONCoordinate = TypedDict("JSONCoordinate", {"row#": int, "column#": int})

# ==========
# https://course.ccs.neu.edu/cs4500f22/4.html

# Interpretation: Describes the direction in which a player may slide the tiles of a row
# or column. For example, "LEFT" means that the spare tile is inserted into the
# right side, such that the pieces move to the left, and the
# left-most tile of the row drops out.
JSONDirection = Union[Literal["UP"], Literal["RIGHT"], Literal["DOWN"], Literal["LEFT"]]

# Interpretation: Describes the four possible counter-clockwise rotations around
# the center of a tile.
JSONDegree = Union[Literal[0], Literal[90], Literal[180], Literal[270]]

# Interpretation: Specifies the last sliding action that an actor
# performed.
JSONAction = List[Union[int, JSONDirection]]

# Interpretation: Specifies the last sliding action that an actor
# performed; None indicates that no sliding action has been performed yet.
OptionalJSONAction = Optional[JSONAction]

# Interpretation: Describes a color which is either a named color, or an RGB value
# matching the regex COLOR_REGEX
JSONColor = str


class JSONPlayer(TypedDict):
    """
    Interpretation: Describes a player's current location, the
    location of its home, and the color of its avatar.
    """
    current: JSONCoordinate
    home: JSONCoordinate
    color: JSONColor


# Interpretation: describes a spare tile
JSONTile = TypedDict("JSONTile", {"tilekey": JSONConnector, "1-image": JSONGem, "2-image": JSONGem})


class JSONState(TypedDict):
    """
    Interpretation: Describes the current state of the board; the spare tile; the
    players and in what order they take turns (left to right); and the last
    sliding action performed (if any). The first item in `plmt` is the
    current player.

    Constraints:
        - `plmt` must be non-empty
        - The colors of any two players in `plmt` must be different
    """
    board: JSONBoard
    spare: JSONTile
    plmt: List[JSONPlayer]
    last: OptionalJSONAction


# ==========
# https://course.ccs.neu.edu/cs4500f22/5.html

# Interpretation: Represents a strategy that a player can follow
JSONStrategyDesignation = Union[Literal["Euclid"], Literal["Riemann"]]

# Interpretation: Denotes that the player wants to pass
JSONChoicePass = Literal["PASS"]

# Interpretation: a list of 4 values
#  - [0] is an int that describes which row or column the player wishes to slide
#  - [1] is a JSONDirection that describes the slide direction
#  - [2] is an int that describes number of degrees by which the spare tile is rotated (counter-clockwise)
#    before it is inserted into the freed-up spot on the board
#  - [3] is a JSONCoordinate that describes the place the player wants to move its avatar
JSONChoiceMove = List[Union[int, JSONDirection, JSONCoordinate]]

# Interpretation: Spells out the two alternatives of a player's response
JSONChoice = Union[JSONChoicePass, JSONChoiceMove]

# ==========
# https://course.ccs.neu.edu/cs4500f22/6.html

# Interpretation: A list of two values
#   - [0] is a string that specifies the name of a player
#   - [1] is a JSONStrategyDesignation for the strategy the named player employs
# Constraint: the name must match NAME_REGEX
JSONPlayerSpecElement = List[Union[str, JSONStrategyDesignation]]

# Interpretation: Describes a list of players
# Constraint: The names of any two different JSONPlayerSpecElements must be distinct.
JSONPlayerSpec = List[JSONPlayerSpecElement]


class JSONRefereePlayer(JSONPlayer):
    """
    Interpretation: Describes a player's current location, its home, its current goal, and the Color of its avatar.
    NOTE: inheriting from a TypedDict carries along its fields (in this case "current", "home", and "color")
    """
    goto: JSONCoordinate


class JSONRefereeState(TypedDict):
    """
    Interpretation: represents the knowledge of the referee at the beginning of a round and before any player has
    reached any assigned goal. Remember that a state's "plmt" field specifies the order in which players take turns.

    Constraint: These coordinates satisfy the conditions of the game, meaning the values of the "home" and "goto"
    fields are on fixed tiles.
    """
    board: JSONBoard
    spare: JSONTile
    plmt: List[JSONRefereePlayer]
    last: OptionalJSONAction


# ==========
# https://course.ccs.neu.edu/cs4500f22/7.html

# Interpretation: One of a player's public methods, which is instructed to behave badly
JSONBadMethod = Union[Literal["setup"], Literal["takeTurn"], Literal["win"]]

# Interpretation: Requests a test with a player acting badly. It is a list of 3 values.
#   - [0] is a string that specifies the name of a player
#   - [1] is a JSONStrategyDesignation for the strategy the named player employs
#   - [2] is a JSONBadMethod that specifies the bad method
#
# The player behaves normally until the bad method is called, at which point it
# integer-divides 1 by 0, raising an exception.
JSONBadPlayerSpecElement = List[Union[str, JSONStrategyDesignation, JSONBadMethod]]

# Interpretation: Describes a list of players, some of whom may behave badly
# Constraint: The names of any two different elements must be distinct.
JSONBadPlayerSpec = List[Union[JSONPlayerSpecElement, JSONBadPlayerSpecElement]]
