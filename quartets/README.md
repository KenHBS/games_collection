# Quartets

Even though playing this game is no fun at all, programming it has been a lot of fun. It's a great way to practice your programming and also serves as a great programming challenge for job interviews!

This implementation of quartets is for the 4-player quartet with 5 quartets. Running a simulation will generate a log file, which contains logs of each move, the subsequent state of the game and, of course, the winner of the game. 

## How to run

While programming this game, I got carried away a little bit and decided to implement different playing policies that a player can choose from.

### Naive game

I consider this the minimum solution, because it shows a solution in the Python sense, without "cluttering" the code  with game decision tactics and memory representations.

You can simulate one of these games by running

```bash
$ python3 naive.py
```
This will create a log file `logs/naive.log`

### Clever game 

This implementation adds decision policies to the `Player` instances. Some of these decision policies apply simple rules that rely on knowledge gained during a game (who owns which cards, etc.). I like this implementation, because it allows me to check whether a clever policy actually makes a big difference in terms of who will win the game: it does matter! Hence I can apply a clever policy to my avater whilst leaving my imaginary opponents with the naive strategy :hankey:

You can simulate one of these games by running

```bash
$ python3 clever.py
```

If you run the clever decision implementation like this, the policies (`random`, `semi-random` and `pretty-smart`) are assigned randomly to the players.  You will find each player's decision policy at the top of `logs/clever.log`

## What does a game look like?
Playing a round of (clever) quartets with my buddies Powpow, Lucky Luke and Donald Duck looks something like this
```
Players at the table: Lucky Luke, Ken, Donald Duck, Powpow
Lucky Luke's policy: semi-random
Ken's policy: pretty-smart
Donald Duck's policy: random
Powpow's policy: pretty-smart
Let the games begin!

Starting round # 1 ...
Lucky Luke: [B-3, B-4, E-2, C-1, A-4]
Ken: [D-4, E-1, D-3, E-4, D-1]
Donald Duck: [C-3, D-2, C-2, A-2, B-1]
Powpow: [E-3, B-2, A-1, A-3, C-4]
Lucky Luke can ask for 11 cards
Lucky Luke asks Powpow: B-1
Powpow does not have B-1
Next round it will be Powpow's turn

Starting round # 2 ...
Lucky Luke: [B-3, B-4, E-2, C-1, A-4]
Ken: [D-4, E-1, D-3, E-4, D-1]
Donald Duck: [C-3, D-2, C-2, A-2, B-1]
Powpow: [E-3, B-2, A-1, A-3, C-4]
Powpow can ask for 11 cards
Powpow asks Lucky Luke: A-4
Powpow gets A-4 from Lucky Luke
Next round it will be Powpow's turn

...
...

Starting round # 19 ...
Lucky Luke: []
Ken: []
Donald Duck: [C-3]
Powpow: [C-4, C-2, C-1]
Powpow can ask for 1 cards
Powpow asks Donald Duck: C-3
Powpow gets C-3 from Donald Duck
Powpow has a quartet with C!
Powpow is putting down [C-4, C-2, C-1, C-3]

The game finished after 19 rounds!
Lucky Luke has 1 quartets
Ken has 2 quartets
Donald Duck has 0 quartets
Powpow has 2 quartets
```
