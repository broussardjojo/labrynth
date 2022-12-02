**If you use GitHub permalinks, make sure your link points to the most recent commit before the milestone deadline.**

## Self-Evaluation Form for Milestone 9

Indicate below each bullet which file/unit takes care of each task.

Getting the new scoring function right is a nicely isolated design
task, ideally suited for an inspection that tells us whether you
(re)learned the basic lessons from Fundamentals I, II, and III. 

This piece of functionality must perform the following four tasks:

- find the player(s) that has(have) visited the highest number of goals
- compute their distances to the home tile
- pick those with the shortest distance as winners
- subtract the winners from the still-active players to determine the losers

The scoring function per se should compose these functions,
with the exception of the last, which can be accomplised with built-ins. 

1. Point to the scoring method plus the three key auxiliaries in your code.

   The scoring method is `State.get_closest_players_to_victory`:
   https://github.khoury.northeastern.edu/CS4500-F22/mysterious-mice/blob/8ddf8d6543d4725e7186ca4914bb07a88da50ce9/Maze/Common/state.py#L153-L165

   **Task 1**: find the player(s) that has(have) visited the highest number of goals. This is not factored out to a
   helper; the main scoring method does it in-line. \
   **Task 2**: compute their distances to the home tile. This is one of the two responsibilities of the
   helper `State.__get_closest_players_to_goal_or_home`:
   https://github.khoury.northeastern.edu/CS4500-F22/mysterious-mice/blob/8ddf8d6543d4725e7186ca4914bb07a88da50ce9/Maze/Common/state.py#L167-L185 \
   **Task 3**: pick those with the shortest distance as winners. This is the second responsibility of the
   helper `State.__get_closest_players_to_goal_or_home`

2. Point to the unit tests of these four functions.

   Only the scoring method `State.get_closest_players_to_victory` is public. The helper is not tested.
   https://github.khoury.northeastern.edu/CS4500-F22/mysterious-mice/blob/8ddf8d6543d4725e7186ca4914bb07a88da50ce9/Maze/Common/test_state.py#L376-L454

The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality, say so.

