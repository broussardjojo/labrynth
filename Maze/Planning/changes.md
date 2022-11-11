TO: CS4500

FROM: Dylan Burati and Thomas Mactaggart

DATE: 11/10/2022

SUBJECT: Analysis of Suggested Changes

### Change 1: Blank Tiles for the Board

**Difficulty Rating: 1**. To accomplish this change we would need to add a new
implementation of the Shape abstract class which would initialize all 4 paths to False. 
We would have to determine some way of representing this as a connector for serialization/deserialization purposes. 
For the sake of "fair" gameplay we might consider adding a constraint to State that no player goal/home can be on
a blank Tile.

### Change 2: Use movable Tiles as goals

**Difficulty Rating: 3**. To accomplish this change we would update the State's knowledge of goal positions in a similar
way that we currently update its knowledge of player positions after slide actions. We would have to modify the
data type for goals to a `Maybe[Position]` to account for the case when a player's goal Tile is the spare Tile.
We would also have to account for the case where a player's goal is not currently on the board (when a Strategy selects
a move and when we rank players by distance to their next goal).

### Change 3: Players pursue multiple goals in order

**Difficulty Rating: 2**. To accomplish this change we would update the Player's data type for goal position to store a 
queue of goals. We would then use the goal queue in the State's goal related methods and replace instances of
incrementing the number of goals a player has reached with a pop from the queue. We would know a player
has reached all their goals when their queue is empty.

Thank you,

Dylan and Thomas
