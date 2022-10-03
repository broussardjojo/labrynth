TO: CS4500

FROM: Diana Rodriguez and Thomas Mactaggart

DATE: 9/29/2022

SUBJECT: Sprints

Given the components of the Maze project, we believe the first three sprints should be defined as follows:

Our goal for sprint one will be to form data representations and visualizations of the basic game pieces. This includes
the tiles, the treasures, the board, and the players' castles and avatars. We intend to model behavior and information
related to game pieces as well as creating visualizations of the pieces during this time. Additionally, each component
will be unit tested and documented.

Our goal for the second sprint will be to create the data representation of a player and their implementation. This will utilize
some of the data representations created in the first sprint, such as the player avatar and castle, to specify player traits.
Players will also have a goal gem, which will utilize the gem data from the first sprint. The player model will also be
responsible for sign ups and pay outs. While the players may not be directly responsible for handling win conditions and directing 
pay outs, they must be able to receive pay outs and pay entry fees. 

Our goal for the third sprint will be to create the player-referee interface. This interface should encode the rules of
the game, such as the roles of the referee and the player. The interface itself should have no visual aspect but should
be able to enforce the actions that players and referees can take. This relates to the first sprint's goals because it
will utilize the data representations established to specify exactly which actions can be taken. For example, the interface
will be able to specify how a tile moves during a turn and how a player's avatar moves, so it will be important that we 
have established these representations already. It will relate to the second sprint's goals because the player model will
allow us to test this interface. 

Given the size of the task at hand, we believe it would be overly ambitious to complete the entire game as robust software 
in three sprints. The next logical step after what has been specified would be to implement referees, then observers, 
and finally remote player communication.
