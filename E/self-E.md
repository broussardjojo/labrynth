## Self-Evaluation Form for TAHBPL/E

A fundamental guideline of Fundamentals I and II is "one task, one
function" or, more generally, separate distinct tasks into distinct
program units. Even exploratory code benefits from this much proper
program design. 

This assignment comes with three distinct, unrelated tasks.

So, indicate below each bullet which file/unit takes care of each task:


1. dealing with the command-line argument (PORT)

    Where we taking in the command-line argument and pass it to the python function:
    https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/52e14c29e509c45b33516855c068c9b6e9abd174/E/xtcp#L2
    
    Where we parse the command-line argument in python:
    https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/52e14c29e509c45b33516855c068c9b6e9abd174/E/Other/xtcp.py#L37

    In python, this is one line of code, so we didn't think it was worth factoring out since that would end up being more lines of code.

2. connecting the client on the specified port to the functionality

    https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/52e14c29e509c45b33516855c068c9b6e9abd174/E/Other/xtcp.py#L38-L41

    We didn't factor out this functionality.

3. core functionality (either copied or imported from `C`)

    https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/52e14c29e509c45b33516855c068c9b6e9abd174/E/Other/xtcp.py#L7-L33


The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request. If you did *not* factor
out these pieces of functionality into separate functions/methods, say
so.

