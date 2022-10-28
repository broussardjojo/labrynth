**If you use GitHub permalinks, make sure your link points to the most recent commit before the milestone deadline.**

## Self-Evaluation Form for Milestone 5

Indicate below each bullet which file/unit takes care of each task:

The player should support five pieces of functionality: 

- `name` : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Players/player.py#L12-L19
- `propose board` (okay to be `void`) : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Players/player.py#L160-L175
- `setting up` : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Players/player.py#L136-L158
- `take a turn` : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Players/player.py#L106-L112
- `did I win` : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Players/player.py#L128-L134

Provide links. 

The referee functionality should compose at least four functions:

- setting up the player with initial information : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/referee.py#L174-L181
- running rounds until termination : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/referee.py#L143-L172
- running a single round (part of the preceding bullet) : We do not have a function to run a single round, we embedded that code into our previous function: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/referee.py#L153-L169
- scoring the game : We don't think we have a score method, it depends what the definition of score is, if by scoring the game
you mean informing the winning players it is here: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/referee.py#L220-L226
if that was not what you meant, we do not have any scoring.

Point to two unit tests for the testing referee:

1. a unit test for the referee function that returns a unique winner : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/test_referee.py#L211-L214
2. a unit test for the scoring function that returns several winners : https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/ce0248c88a6cbef30483a6c44a895dabbbdeba0a/Maze/Referee/test_referee.py#L284-L290

The ideal feedback for each of these points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files -- in the last git-commit from Thursday evening. 

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality, say so.

