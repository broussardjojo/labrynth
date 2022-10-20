Pair: mactaggartt-rodriguezdia \
Commit: [32acda181e733db1664bb2e0cd920c358331ddfa](https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/tree/32acda181e733db1664bb2e0cd920c358331ddfa) \
Self-eval: https://github.khoury.northeastern.edu/CS4500-F22/mactaggartt-rodriguezdia/blob/97709704c1e072606429fdb838af4c466a72617c/3/self-3.md \
Score: 50/85 \
Grader: Mike Delmonaco

## Programming (20 pts self-eval, 45 pts code):

Good job providing links to the right commit on your self eval.

The purpose of `State#slide_and_insert` should specify that the spare tile is inserted. Since it's clear from the name, I'll "let it slide".

-6 (self eval points) Misdirecting for "move the avatar of the currently active player to a designated spot". You didn't implement this in the state.
If you don't implement something, say so. You will get partial credit, rather than being penalized for misdirecting.

-5 (code points) (same issue as above). It should be possible to perform this action by calling methods on the game state only.

-14 (rest of self eval points) Misdirecting for "check whether the active player's move has returned its avatar home". You didn't implement this.

-5 (code points) (same issue as above)

I might have taken points off for misdirecting on your shift/insert unit tests, but you already lost all of your accuracy points. You linked to board tests, when
you should've said that you didn't test this on the state, only the board. Being explicit and clear for something like that is important.

## Design (20 pts):

The referee will drive communication. It will send information to and request information from the player, not the other way around.

How would the player know about the board? This is not accounted for in your design as written.

-5 No method for the referee to request a move from the player
