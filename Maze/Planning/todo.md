## Milestone 7 - The Clean Up

### Priority: Very High

- [ ] Fix Makefile
  - The file 6/requirements.txt locks package versions which aren't compatible with
    Python 3.6. The console error is `Could not find a version that satisfies the requirement importlib-metadata==5.0.0 (from -r requirements.txt (line 2))`

### Priority: High

- [ ] The strategy should attempt to reach a `Position`, not a `Tile`
  - Rationale: Course website update on October 26th during milestone 5:
    - > If you tried to go to specific (unique) tiles instead of specific coordinates, please change your code to match the now clarified specification.
  - Rationale 2: `Board.get_position_from_tile` is a performance bottleneck, checking 49
    tiles for equality. We already track players' current location, so this can be avoided.
  - [ ] Eliminate need for `Board.get_position_from_tile`. While doing this we can add an intermediate data structure which will allow us to more easily abstract `Board.slide*` and more easily implement player position tracking.
  - [ ] Change signature of `Board.reachable_tiles` to take in Position
  - [ ] Update signatures of `BaseStrategy` to avoid dependency on specific Tile

&nbsp;

- [ ] The Referee should interact with an `APIPlayer`, distinct from the class `Player` which holds info like current position, home position, and color
  - Rationale: Implementing the logical interactions is a separate task from managing a player's knowledge about the game
  - [ ] Create `APIPlayer`
  - [ ] Use `asyncio` to simulate the player living across the network, add acknowledgments from the player (no more void methods in player interactions)
  - [ ] Write a remote proxy wrapper for the `APIPlayer` which handles timeout errors and safety errors
  - [ ] Update referee to wrap all `APIPlayer` instances in its constructor, and replace thread logic
  - [ ] While fixing this also inform losing players

- [ ] Use the observer pattern for `Observer`
  - [ ] Define the observer interface
  - [ ] Update the current observer to be a `GUIObserver`, implementing `Observer`
  - [ ] Test referee interactions with an observer, using a different implementation

&nbsp;

- [ ] There should be a `State` implementation which a `Strategy` can use to explore possible moves. It must not have access to any secrets.
  - Rationale: `Strategy` currently accesses many board methods, and implements its own player position tracking. It also contains its own logic to ensure that the avatar move actually moves the player on the reconfigured board.
  - [ ] Split `Player` into a class that only holds publicly known info, and a `PlayerWithSecret` class which stores a `Player` and its list of unvisited goals.
  - [ ] Create a base version of a state which handles only board operations, and leaves the helpers to manage player information unimplemented
    - `get_players`: abstract
    - `rotate_spare_tile`: does not depend on player list
    - `slide_and_insert`: modifies player list via abstract helper `_adjust_all_players`
    - `legal_slides`: does not depend on player list
    - `legal_destinations`: does not depend on player list; uses `Board.reachable_tiles`
    - `begin_transaction`: 
  - [ ] Create superclass of above for `APIPlayer` and `Strategy`, storing a list of `Player` objects only
  - [ ] Update `Strategy` to use this implementation
  - [ ] Create superclass of above for `Referee`, storing a list of `PlayerWithSecret`, and providing an additional method to retrieve that


### Priority: Medium

- [ ] Install a JSON library which can parse data as it arrives, instead of requiring it all at once.

- [ ] All non-test code should be 100% typed, and avoid the `Any` type

- [ ] `Move` combinators should be rewritten to make the "first-non-pass" preference of the two strategies more clear.
  - Rationale: The dynamic dispatches surrounding `Move` and `Pass` force the reader to jump through multiple call points to understand fairly simple code.
  - [ ] Build a utility union type `Maybe[T]`, and represent `Pass` as the empty variant, and a `Move` as the non-empty one
  - [ ] Create a utility function to find the first non-empty `Maybe` in a stream (Generator)
  - [ ] Refactor dynamic dispatch in `Referee` to improve readability

- [x] `State` should not allow adding players
  - Rationale: All players should be registered before gameplay begins

- [ ] `Observer` should 

### Priority: Low

- [ ] Multiple sources of truth: `check_stationary_position` should use `can_slide`
- [ ] On classes we've written, `__hash__` can just use a tuple instead of doing math with multiple results
- [ ] Get linter IDE support working
- [ ] Remove `multipledispatch`
- [ ] Make `get_opposite_direction` from utils an actual method on a Direction
- [ ] The file checking in `Gem` can be cached


### Completed

- [x] `State` should not allow adding players (MEDIUM)
  - Rationale: All players should be registered before gameplay begins
  - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/3698168acf8fd1f130aabbf1a0c08ce386814371
  - Commit Message: **remove ability to add players to state**