**If you use GitHub permalinks, make sure your link points to the most recent commit before the milestone deadline.**

## Self-Evaluation Form for Milestone 8

Indicate below each bullet which file/unit takes care of each task.

For `Maze/Remote/player`,

- explain how it implements the exact same interface as `Maze/Player/player`

The class `RemotePlayer` implements the actual `APIPlayer` interface: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Remote/player.py#L14
Each method call on a `RemotePlayer` is translated by `RemotePlayerMethod.call` to a serialization + JSON write, followed by a JSON read + deserialization + type validation. 

- explain how it receives the TCP connection that enables it to communicate with a client

https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Remote/player.py#L36-L42
A `RemotePlayer` can use any generator of JSON values as its input channel, and any file-like object as its output
channel. The above link shows a convenience method which uses a socket to provide both. 

- point to unit tests that check whether it writes JSON to a mock output device

We do not have any tests with a mock output device; our unit tests use both a `RemotePlayer` and `DispatchingReceiver` which
actually communicate over a socket. This unit test ensures that malformed JSON is rejected by the `RemotePlayer`: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Remote/test_remote_player.py#L191-L217 

For `Maze/Remote/referee`,

- explain how it implements the same interface as `Maze/Referee/referee`

Our `DispatchingReceiver` is not related to a referee, aside from the fact that it uses an APIPlayer.

- explain how it receives the TCP connection that enables it to communicate with a server

https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Remote/referee.py#L31-L38
A `DispatchingReceiver` can use any generator of JSON values as its input channel, and any file-like object as its output
channel. The above link shows a convenience method which uses a socket to provide both. 

- point to unit tests that check whether it reads JSON from a mock input device

We do not test the `DispatchingReceiver` as its own unit, as we considered it a part of our remote player testing.

For `Maze/Client/client`, explain what happens when the client is started _before_ the server is up and running:

- does it wait until the server is up (best solution)

No.

- does it shut down gracefully (acceptable now, but switch to the first option for 9)

The Client component will raise an OSError when `socket.create_connection` fails, but it will release all resources.
The current code expects the creator of the client to catch or suppress this error, as we do in the example `main`: https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Client/client.py#L65-L70

For `Maze/Server/server`, explain how the code implements the two waiting periods:

- is it baked in? (unacceptable after Milestone 7)

No.

- parameterized by a constant (correct).

The server hardcodes the *number of waiting periods* (2), and uses a constant for their duration:
https://github.khoury.northeastern.edu/CS4500-F22/salty-dolphins/blob/e82b73239854de428c2d522bc29e263f5121f5c5/Maze/Server/server.py#L35

The ideal feedback for each of these three points is a GitHub
perma-link to the range of lines in a specific file or a collection of
files.

A lesser alternative is to specify paths to files and, if files are
longer than a laptop screen, positions within files are appropriate
responses.

You may wish to add a sentence that explains how you think the
specified code snippets answer the request.

If you did *not* realize these pieces of functionality, say so.

