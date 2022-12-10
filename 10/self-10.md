**If you use GitHub permalinks, make sure your link points to the most recent commit before the milestone deadline.**

## Self-Evaluation Form for Milestone 10

We wil _not_ inspect your code for this milestone due to a lack of TA manpower. 

Task:
```
If you haven’t done so, harden the existing remote-proxy player against ill-formed and invalid JSON. This revision is for optional credit.
```

Our components are protected from invalid / malformed JSON during the steady state phase of the game because all 
internetwork communication takes place through our [RemotePlayerMethods](https://github.khoury.northeastern.edu/CS4500-F22/mysterious-mice/blob/1a03152abacc16448641f23feca7cbbc86b3f969/Maze/Remote/remote_player_methods.py).
From our [README](https://github.khoury.northeastern.edu/CS4500-F22/mysterious-mice/blob/1a03152abacc16448641f23feca7cbbc86b3f969/Maze/Readme.md),

>The RemotePlayerMethod deals with all of the conversion into and out of our classes (Position, State, Move, Pass, etc.). Functions called serialize_* above don't fully convert to bytes but instead give back some kind of Jsonable, which we have many of in our JSON/definitions.py file. The same is true for inputs to deserialize_*.
>We are protected from malformed JSON by an ijson.items object, which will never give us a non-Jsonable, but instead throw IncompleteJSONError. We are protected from invalid JSON by pydantic, which will confirm that the shape of the Jsonable matches our JSON type definition, or else throw a ValidationError.
>These errors are then caught by gather_ or await_protected, and the Referee can check the Maybe[TResult] is_present to differentiate success from failure (timeout is also a failure).
