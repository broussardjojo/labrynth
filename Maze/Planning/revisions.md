## Revisions

- Required revisions
    - Support a shared `additional_goals` list in `Referee`
        - Write a application-wide `Config` class to control whether the revision is active (also a good place for
          timeouts and other constants)
        - Refactor the state creators used by `run_game` to assign initial goals and return the unused ones
        - Refactor the `run_game_from_state` method to use a helper that determines unused goals
            - We know from data definitions that `RefereeState` represents a game before any goals have been reached
    - Inform players of new goals using a `setup(None, \<position>)` call whenever they reach their goal
        - Add boolean attribute `RefereePlayerDetails._is_goal_ultimate`, because `State` can no longer use a player's
          number of goals reached to determine whether the player's goal should be their last one
        - Set `RefereePlayerDetails` goal position if a player lands on their goal. The spec states that this should
          pull from `additional_goals` if it's non-empty, and otherwise give the player their home position as their
          last target
            - Currently working with belief that if the goal is sent from the Referee with setup it can not remain
              in `additional_goals` [(source)](https://piazza.com/class/l7g9e46cc2l4d3/post/224)
            - Refactor `State.is_active_player_at_goal` into `update_active_player_goals_reached`, which can only be
              called once per turn, and make `is_active_player_at_goal` a side-effect-free method
        - Fix bug introduced by above change; the `set_goal_position` call means that any subsequent calls
          to `did_active_player_end_game` on the same turn can be wrong, so we check `did_active_player_end_game` first

- Semi-related changes
    - Create `SafeAPIPlayer` to protect against the type of bug where the caller (`Referee`) forgets to treat its
      `APIPlayer`s as untrusted components
        - This was also a convenient place to implement a teardown hook that interrupts ongoing I/O operations for
          remote players. These would otherwise continue indefinitely, because `gather_protected` can not halt threads
          that time out before giving back a value. Additionally, the base `socket.close()` method is not thread-safe,
          so we needed to create a `ReadableStreamWrapper`
    - Eliminate `Referee`'s `did_active_player_cheat` and move the actual `handle_cheater` call to a single point
      in `__run_round`
        - This was the reason we created `MoveReturnType`, an enum of the cases `KICK`, `MOVED`, and `PASSED`
