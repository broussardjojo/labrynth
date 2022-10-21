**If you use GitHub permalinks, make sure your links points to the most recent commit before the milestone deadline.**

## Self-Evaluation Form for Milestone 4

The milestone asks for a function that performs six identifiable
separate tasks. We are looking for four of them and will overlook that
some of you may have written deep loop nests (which are in all
likelihood difficult to understand for anyone who is to maintain this
code.)

Indicate below each bullet which file/unit takes care of each task:

1. the "top-level" function/method, which composes tasks 2 and 3 

https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/base_strategy.py#L124-L147

2. a method that `generates` the sequence of spots the player may wish to move to

Method declared in the abstract class: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/base_strategy.py#L46-L53

Implementation in Riemann: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/riemann.py#L29-L43

Implementation in Euclid: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/euclid.py#L42-L62

3. a method that `searches` rows,  columns, etcetc. 

https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/base_strategy.py#L78-L105

4. a method that ensure that the location of the avatar _after_ the
   insertion and rotation is a good one and makes the target reachable

We do not have a method that performs this action, we included this check inline in our searching method from
question 3, here is the block of code which does this within our searching method: 

https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/base_strategy.py#L97-L102

ALSO point to

- the data def. for what the strategy returns

https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/move.py#L7-L14

- unit tests for the strategy

Here is our test euclid file: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/test_euclid.py

here is our test riemann file: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/e285b5126a5daa432cc7afe89806b14b25f45c19/Maze/Players/test_riemann.py

The ideal feedback for each of these points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality or realized
them differently, say so and explain yourself.


