Pair: mactaggartt-rodriguezdia \
Commit: [e285b5126a5daa432cc7afe89806b14b25f45c19](https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/tree/e285b5126a5daa432cc7afe89806b14b25f45c19) \
Self-eval: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/9b9c51c5897eb57ada8ca81a0cc970237fbc69d8/4/self-4.md \
Score: 89/110 \
Grader: Ryan Jung

- [10/10] for an accurate self eval.

- Checking for a good name, signature/types, and purpose statement for the following:
  - [15/15] for a top level method that composes tasks 2 and 3.

  - [15/15] for `get_next_target_position`, which generates a sequence of spots the player may wish to move to.
    NOTE: what is the runtime complexity of this method?

  - [15/15] for a method that searches row then columns.

  - [9/15] admits they did not write a method that ensure that the location of the avatar after the insertion and rotation is a good one and makes the target reachable

- [5/20] for the return type of a strategy; deduction for move object that has a boolean flag indicating if it is one of two options. Constructing a "pass" in this codebase means building a move with nonsensical arguments. Similarly, a move will require a redundant boolean False argument.

- [10/10] for a test that produces an action to move the player.

- [10/10] for a test that forces the player to skip their turn.

Great tests!

## Design (ungraded)

How would a referee add players to the game to start? How would it know who the players are?

The discussion over how the referee validates moves and interacts with the game state are irrelevant. We care about the ref-player protocol.

This design document fails to address how the referee and player interact. It is nonsensical to have a protocol in which the player never communicates to the referee.

Finally, the memo does not make use of the data language of your choice or a UML diagram as suggested. While not required, it would make your spec easier to read and easier to write.

Reread the assignment. This would get a zero if graded.


Linked to post-deadline commit e285b5126a5daa432cc7afe89806b14b25f45c19 from 10-21 12:03 AM
