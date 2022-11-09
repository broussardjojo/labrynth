## Required capabilities

- `State` can kick out the active player without a `Referee` involved
    - When this happens, the state must know the next active player
- `Referee` can kick out a player regardless of whether they're active or not

## Option 0

Ref's `List[APIPlayer]` and State's `List[Player]` in lockstep AND use `active_player_index` to mean the `Player` we
care about at the moment.

- Needs:
    - `Referee.handle_broadcast_result(List[Maybe[Acknowledgement]])` which does a `kick` for every failure and a
      `change_active` for every success
    - Not strictly necessary but maybe
        - `State.reset_active_player_index()` to go back to 0, so that `win` does the above correctly

## Option 1

Ref's `List[APIPlayer]` and State's `List[Player]` in lockstep

- Needs: `{Referee,State}.kick_out_player_at_index(int)`
- Cons:
    - Index math; if we have multiple players to kick out, we would need to call the method on the indices to kick in
      descending order

## Option 2

Ref's `Dict[ID, APIPlayer]` has equivalent key set with State's `Dict[ID, Player]`. State also has a `List[ID]`

- Needs: `{Referee,State}.kick_out_player_by_id(ID)`
- Pros:
    - Keeping key set synced doesn't require index math; as long as Referee's kick calls State's kick, the
      collections will never differ
    - Since State uses `get_active_player()` internally, it's easy enough to convert `players[i]`
      to `player_map[ids[i]]`
- Cons:
    - The IDs are in lockstep in 3 places

## Option 3

Players have an ID field. Ref's `Dict[Player, APIPlayer]` maps every player to its client.

- Needs: `Player.__hash__`, `Player.__eq__`, `State.kick_out_player(Player)`
- Pros:
    - Same as option 2, but not even a minimal change in `State`
- Cons:
    - Lose-lose: either the `color` becomes the ID and we depend on the vague uniqueness mentions in the spec,
      or a new field is added and we have to decide where/how to generate it.
    - Blocks potential for Player to represent _just_ board and game logic
        - `deepcopy(player1) == player1.set_current_position(...)`

## Option 4

State takes in a mutable view of a list which might be shared with the referee.

```
BasePlayerSequence(ABC):
    @abstractmethod
    def get(self, index: int) -> Player: pass
    
    @abstractmethod
    def remove(self, index: int) -> None: pass

PlayerSequence(BasePlayerSequence):
    __data: List[Player]

PlayerAndClientSequence(BasePlayerSequence):
    __data: List[Tuple[Player, APIPlayer]]
    
    def remove_many(self, ...) -> None:
        ...
```

- Cons:
    - Difficult to do something with the player name after
    - Multiple components are responsible for actually calling `remove` (`Referee` during setup and scoring, `State`
      during gameplay)
