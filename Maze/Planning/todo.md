## Milestone 7 - The Clean Up

### Priority: Very High

All done! 🎉

### Priority: High

We intend to complete this TODO between submission of Milestone 7 and beginning work on Milestone 8
- [ ] Use the observer pattern for `Observer`
    - [ ] Define the observer interface
    - [ ] Update the current observer to be a `GUIObserver`, implementing `Observer`
    - [ ] Test referee interactions with an observer, using a different implementation

&nbsp;

We intend to complete this TODO between submission of Milestone 7 and beginning work on Milestone 8
- [ ] There should be a `State` implementation which a `Strategy` can use to explore possible moves. It must not have
  access to any secrets.
    - Rationale: `Strategy` currently accesses many board methods, and implements its own player position tracking. It
      also contains its own logic to ensure that the avatar move actually moves the player on the reconfigured board.
    - [ ] Split `Player` into a class that only holds publicly known info, and a `PlayerWithSecret` class which stores
      a `Player` and its list of unvisited goals.
    - [ ] Create a base version of a state which handles only board operations, and leaves the helpers to manage player
      information unimplemented
        - `get_players`: abstract
        - `rotate_spare_tile`: does not depend on player list
        - `slide_and_insert`: modifies player list via abstract helper `_adjust_all_players`
        - `legal_slides`: does not depend on player list
        - `legal_destinations`: does not depend on player list; uses `Board.reachable_tiles`
        - `begin_transaction`:
    - [ ] Create superclass of above for `APIPlayer` and `Strategy`, storing a list of `Player` objects only
    - [ ] Update `Strategy` to use this implementation
    - [ ] Create superclass of above for `Referee`, storing a list of `PlayerWithSecret`, and providing an additional
      method to retrieve that

### Priority: Medium


- [ ] Install a JSON library which can parse data as it arrives, instead of requiring it all at once.

We intend to complete this TODO between submission of Milestone 7 and beginning work on Milestone 8
- [ ] `Move` combinators should be rewritten to make the "first-non-pass" preference of the two strategies more clear.
    - Rationale: The dynamic dispatches surrounding `Move` and `Pass` force the reader to jump through multiple call
      points to understand fairly simple code.
    - [ ] Build a utility union type `Maybe[T]`, and represent `Pass` as the empty variant, and a `Move` as the
      non-empty one
    - [ ] Create a utility function to find the first non-empty `Maybe` in a stream (Generator)
    - [ ] Refactor dynamic dispatch in `Referee` to improve readability
    
### Priority: Low

- [ ] On classes we've written, `__hash__` can just use a tuple instead of doing math with multiple results
- [ ] The file checking in `Gem` can be cached


### Completed

- [x] `State` should not allow adding players (MEDIUM)
    - Rationale: All players should be registered before gameplay begins
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/3698168acf8fd1f130aabbf1a0c08ce386814371
    - Commit Message: **remove ability to add players to state**

- [x] `Shape` should not be mutable (MEDIUM)
    - Rationale: The serializer needs to use `Shape` values as dict keys, and its behavior gets confusing when mutation
      is allowed
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/8afe3f26b7db1cc45b618bc63200e116b7b10fce
    - Commit Message: **Make Shape immutable**

- [x] The strategy should attempt to reach a `Position`, not a `Tile` (HIGH)
    - Rationale: Course website update on October 26th during milestone 5:
        - > If you tried to go to specific (unique) tiles instead of specific coordinates, please change your code to match the now clarified specification.
    - Rationale 2: `Board.get_position_from_tile` is a performance bottleneck, checking 49 tiles for equality. We
      already track players' current location, so this can be avoided.
    - Approach: Eliminate all uses of `Board.get_position_from_tile`.
    - [x] Find a way to improve `Player` position tracking.
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/8c6fc3db26f91ade8e67785e06c3827edae50fab
        - Commit Message: **update board to use new position transition map**
    - [x] Change signature of `Board.reachable_tiles` to take in Position and refactor all related code in `State`
      and `Board`
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/723ea1544a6e6bd0fdbd357ed759b67bd9561e34
        - Commit Message: **update board.reachable_tiles and all code related to it**
    - [x] Update signatures of `BaseStrategy` to avoid dependency on specific Tile
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/80adfaff73ca02efb5e943abfc3d2b3cd43edf43
        - Commit Message: **Update strategy to fully remove position-tile conversions**
        
- [x] The Referee should interact with an `APIPlayer`, distinct from the class `Player` which holds info like current
  position, home position, and color (HIGH)
    - Rationale: Implementing the logical interactions is a separate task from managing a player's knowledge about the
      game
    - [x] Create `APIPlayer`
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/562367b255ff581084e391c925ba0e49cedd1efd
        - Commit Message: **Separate Player from APIPlayer**
    - [x] add acknowledgments from the player (no more void methods in player interactions)
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/562367b255ff581084e391c925ba0e49cedd1efd
        - Commit Message: **Separate Player from APIPlayer**
    - [x] Write a utility function for the `APIPlayer` calls which handles timeout errors and safety errors
        - Commit 1: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/1e99dbef7b8b62c83d86de961af965d521c00357
        - Commit 1 Message: **working on timeout handling**
        - Commit 2: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/ddccef39c43f964cfbd454779f6991f8de11d54a
        - Commit 2 Message: **Finish testing thread utils, add docstrings** 
        - Commit 3: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/37dcc2af47a232f6431077f6f502e25876bae726
        - Commit 3 Message: **implement timeout and safety handling for APIPlayers**
    - [x] Use threading to simulate an untrusted/remote player
        - Commit 1: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/37dcc2af47a232f6431077f6f502e25876bae726
        - Commit 1 Message: **implement timeout and safety handling for APIPlayers**
        - Commit 2: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/27d6007c16f2df886df7980dd8c618c9371f300c
        - Commit 2 Message: **fix buggy test**
        - Commit 3: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/fa6d395d1aac1654f963de8599375d69bc5154d9
        - Commit 3 Message: **Write all_valid_players referee test and partially support observers**
    - [x] While fixing this also inform losing players
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/37dcc2af47a232f6431077f6f502e25876bae726
        - Commit Message: **implement timeout and safety handling for APIPlayers**

- [x] Boards are not NxN and are instead MxN (HIGH)
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/505b17a022b37871a55668c5e1b4980216172a1d
    - Commit Message: **allow boards to be size M by N**
  
- [x] Multiple sources of truth: `check_stationary_position` should use `can_slide` (LOW)
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/505b17a022b37871a55668c5e1b4980216172a1d
    - Commit Message: **allow boards to be size M by N**

- [x] Remove `multipledispatch` (LOW)
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/554442ed04d7c6d4cced154f3b983db588bb357a
    - Commit Message: **Begin using APIPlayer in Referee**

- [x] Get linter IDE support working (LOW)
    - No commit for this, completed on ignored file
    
- [x] Make `get_opposite_direction` from utils an actual method on a Direction (LOW)
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/9b0faae9b36dc840169f1b9ef3b217e17a3ff336 
    - Commit Message: **eliminate duplicate implementations of get_opposite_direction**

- [x] Fix deserializers and guard against type errors (VERY HIGH)
    - Using the JSON object list directly is bypassing type hints and causing bugs test failures like this
      one: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/8e6f41ed2867bc7de71b5603d05e245d7878fe51/4/testfest/test-results.txt#L14
    - [x] Create JSON data definitions as Python types
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/925937afcb67fce4134863c48377ac7666d5978a
        - Commit Message: **Add JSON definitions, JSON serializers through milestone 5**
    - [x] Type hint all functions, and avoid the `Any` type
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/925937afcb67fce4134863c48377ac7666d5978a
        - Commit Message: **Add JSON definitions, JSON serializers through milestone 5**
    - [x] Update some harnesses to use well-typed deserializers
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/1718182af0c126219cb4b0674cb457fe972904ef
        - Commit Message: **Write rest of deserializers, create Harnesses packages, implement xbad**

- [x] Organize serializers/deserializers and integration test harnesses (currently the integration test harnesses are in
  the same file as their main data structure's serialization code) (LOW)
   - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/1718182af0c126219cb4b0674cb457fe972904ef
   - Commit Message: **Write rest of deserializers, create Harnesses packages, implement xbad**

- [x] Fix Makefile (VERY HIGH)
    - Rationale: The file 6/requirements.txt locks package versions which aren't compatible with Python 3.6. The console error
      is `Could not find a version that satisfies the requirement importlib-metadata==5.0.0 (from -r requirements.txt (line 2))`
    - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/288d1357ad27430e01cf4b887a05f82ee44b02f1
    - Commit Message: **Use venv in Makefile and new script**

- [x] Fix broken integration tests (VERY HIGH)
    - [x] `xstate` and `xbad` have two failing tests where a player reaches their goal tile, which is also their home tile.
    Our implementation declares them the winner on that turn, when it should wait until they make another turn and land on
    their home.
        - Commit: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/commit/a2a6a7a2f5de7a0840e2fddff8af6b7e94ddb4d5
        - Commit Message: **Fix edge case: must reach goal and home on separate turns**