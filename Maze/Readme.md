# Development and Testing

To run all unit tests for this Milestone run `./xtest`

To run an individual unit test file run `pytest path/to/file`

To run an individual unit test run `pytest path/to/file::test_function_name`

Before running unit tests you may need to run `make` to install project dependencies

When installing packages, ensure that the version is compatible with Python 3.6. The `requirements.txt`
in this directory contains the latest versions of `pytest` and its dependencies which supported Python 3.6.


# Components and Roadmap

### The server side of Maze.com

```ascii
+---------------------------+
| Server                    |   [socket.socket] <~ 
| + signs up players        |
|                           |    
| + manages waiting         |    
|      periods              |    
| + creates referee and     |
|      calls the RunGameFn  |>>>>, 
+---------------------------+    V
                                 V
+---------------------------+    V
| Referee                   |    V
| + accepts added observers |    V
|                           |    V
| + runs game               |<<<<' [SafeAPIPlayer] (implemented by SafeRemotePlayer, a thin wrapper
|    + setup (broadcast)    |                       around RemotePlayer)
|    + runs rounds (many    |    ↱  [State]: ---------+---------------------------+
|       take-turn and setup |     ↲                   | State                     |
|       calls; send)        |                         | + rotates spare, slides & |     
|    + win (broadcast)      |>>>>,                    |      inserts & moves      | 
+---------------------------+    V                    |      active player        | 
                                 V                    |      (via AbstractState)  |  
                                 V                    |                           |  
                                 V                    | + allows move             |  
                      [GameOutcome]                   |       validity checks     |
                                                      |       (via AbstractState) |  
                                                      |                           |  
                                                      | + allows end game check   |  
                                                      | + can kick active player  |
                                                      | + can end turns           |
                                                      | + allows game scoring     |
                                                      +---------------------------+
```

### The client side of Maze.com

```ascii
+---------------------------+
| Client                    | 
| + signs up 1 player       |>>>>,   
+---------------------------+    V
                                 V
                                 V
+---------------------------+    V
| DispatchingReceiver       |    V  APIPlayer and
| + participates through    |<<<<'   (read_channel: Iterator[Any], write_channel: IO[bytes])
|      the stored player    |
+---------------------------+    ↱  [APIPlayer]: -----+---------------------------+
                                  ↲                   | LocalPlayer               |
                                                      | + remembers goal posn     |     
                                                      |                           |     
                                                      | + takes turns by          |  
                                                      |      delegating to        |
+----------------------------+ -----------------------|      Strategy             |  
| BaseStrategy               |                        +---------------------------+
| + iterates through goal    |
|      preference order      |
|      (abstract)            |
|                            |
| + within that, iterates    |
|      through slide pref.   |
|      order and rotation    |
|      preference order      |
|                            |
| + uses given RedactedState |
|      to check move         |
|      validity, returns     |
|      first found           |
+----------------------------+
```

### Remote Interaction

The Server hands off the player list to the referee so that the interactions will look like this from the left-hand
perspective. The Client creates a DispatchingReceiver to that the interactions will look like this from the right-hand
perspective.

```ascii
    Referee               SafeRemotePlayer       RemotePlayer          ============RemotePlayerMethod===========      DispatchingReceiver   LocalPlayer
    |                     |                      |                     |                                       |                        |             |
    |  ->                 |                      |                     |crossing->                   ->crossing|                        |             |
    |  python             |  ->                  |  ->                 |this                               this|    loops               |             |
    |  call               |  submit to executor  |  select one of      |fence                             fence|    using               |             |
    |                     |  <-                  |  the remote         |does                               does|    read, then          |             |
    |                     |  Future[TResult]     |  methods            |`serialize_args`     `deserialize_args`|    RemotePlayerMethods |             |
    |                     |                      |                     |`write`                 `validate_args`|    .respond(Player)    |             |
    |                     |                      |                     |                                       |                        |             |
    |                     |                      |                     |                                       |                        |             |
    |                     |                      |                     |                                       |                        |             |
    |                     |                      |                     |crossing<-                   <-crossing|                        |             |
    |                     |  <-                  |  <-                 |this                               this|                        |             |
    |  <-                 |  (submit finishes,   |  JSONError          |fence                             fence|                        |             |
    |  await_protected    |   waiters on the     |  | ValidationError  |does                               does|                        |             |
    |  turns Future[T]    |   Future are         |  | TResult          |`deserialize_result` `serialize_result`|                        |             |
    |  to Maybe[T]        |   notified)          |                     |`validate_result`               `write`|                        |             |
    |  OR                 |                      |                     |                                       |                        |             |
    |  gather_protected   |                      |                     |                                       |                        |             |
    |  turns Fut[List[T]] |                      |                     |                                       |                        |             |
    |  to Mby[List[T]]    |                      |                     |                                       |                        |             |
```

# Component Interactions

### Server-side

![Server-side](../server-side-diagram.jpg)

### Client-side and remote proxies

![Client-side and remote proxies](../client-and-remote-diagram.jpg)
